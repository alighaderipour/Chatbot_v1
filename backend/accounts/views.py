import openpyxl
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AppSettings, UserProfile
from .pagination import UserPagination
from .permissions import IsAdmin, IsStaffOrAdmin
from .serializers import (
    AppSettingsSerializer,
    MeSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


def _cell_to_str(value):
    """
    Coerce an Excel cell value to a clean string.

    Excel/openpyxl silently stores numeric-looking cells (like a username
    "123") as an actual float unless the column is explicitly formatted as
    Text — which turns into "123.0" if you just str() it directly. This
    catches that specific case.
    """
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()

# Fields that only a true admin (is_superuser) may change — staff can still
# manage regular users' basic info, but promoting/demoting roles or setting
# someone's password is admin-only.
ADMIN_ONLY_FIELDS = {"is_staff", "is_superuser", "password"}


class UserListCreateView(generics.ListCreateAPIView):
    """GET: staff or admin can list all users (paginated). POST: admin-only, creates a new one."""

    queryset = User.objects.all().order_by("username")
    pagination_class = UserPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsStaffOrAdmin()]

    def get_serializer_class(self):
        return UserCreateSerializer if self.request.method == "POST" else UserSerializer


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    GET: staff or admin can view a user.
    PATCH: staff can edit a regular user's name/active-flag/message limit.
           Editing a staff/admin account, or changing is_staff/is_superuser/
           password on anyone, requires admin (IsAdmin).

    Intentionally no DELETE — "inactive" users are handled via
    is_active=False instead, which keeps their conversation history intact
    rather than destroying it.
    """

    queryset = User.objects.all()
    permission_classes = [IsStaffOrAdmin]

    def get_serializer_class(self):
        return UserUpdateSerializer if self.request.method in ("PATCH", "PUT") else UserSerializer

    def patch(self, request, *args, **kwargs):
        target = self.get_object()
        is_admin = request.user.is_superuser

        touches_admin_only_field = any(field in request.data for field in ADMIN_ONLY_FIELDS)
        target_is_privileged = target.is_staff or target.is_superuser

        if not is_admin and (touches_admin_only_field or target_is_privileged):
            return Response(
                {"detail": "Only an admin can do that."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # partial=True is essential here: the frontend intentionally only
        # sends fields the admin actually filled in (see UsersPanel.vue).
        # Without partial=True, DRF would apply model-level defaults to any
        # OMITTED boolean field (is_active/is_staff/is_superuser) instead of
        # leaving it untouched — silently resetting things the admin never
        # meant to change.
        serializer = self.get_serializer(target, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        target.refresh_from_db()
        # Re-serialize with the FULL UserSerializer for the response, since
        # UserUpdateSerializer only outputs the handful of fields it accepts
        # as input (no id/username) — returning that partial shape used to
        # break the frontend's user list (missing :key) and looked like the
        # edited user had vanished until a full page reload.
        return Response(UserSerializer(target).data)


class MeView(generics.RetrieveAPIView):
    """Any authenticated user: fetch their own profile info."""

    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserBulkImportView(APIView):
    """
    Admin-only: POST an .xlsx file with columns named 'username', 'name',
    'family', and optionally 'password' and 'message_limit'.

    - If 'password' is blank/missing for a row, the new user's password
      defaults to their username.
    - If 'message_limit' is blank/missing, that user has no limit.

    Returns a full breakdown (created / skipped-duplicate / skipped-blank /
    errors) with row numbers, so a partial import is always explainable
    instead of silently losing rows.
    """

    permission_classes = [IsAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            workbook = openpyxl.load_workbook(file, read_only=True, data_only=True)
        except Exception:
            return Response(
                {"detail": "Could not read that file — make sure it's a valid .xlsx."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            return Response({"detail": "The file is empty."}, status=status.HTTP_400_BAD_REQUEST)

        header = [str(c).strip().lower() if c else "" for c in rows[0]]
        try:
            username_idx = header.index("username")
            name_idx = header.index("name")
            family_idx = header.index("family")
        except ValueError:
            return Response(
                {"detail": "Expected columns named 'username', 'name', and 'family'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Optional columns — fall back to None if not present in the file.
        password_idx = header.index("password") if "password" in header else None
        limit_idx = header.index("message_limit") if "message_limit" in header else None

        created = []
        skipped_duplicate = []
        skipped_blank = []
        errors = []

        data_rows = rows[1:]

        for offset, row in enumerate(data_rows):
            row_number = offset + 2  # +1 for header, +1 for 1-indexing — matches what you'd see in Excel

            if not row or not row[username_idx]:
                skipped_blank.append(row_number)
                continue

            try:
                username = _cell_to_str(row[username_idx])
                first_name = _cell_to_str(row[name_idx])
                last_name = _cell_to_str(row[family_idx])

                if User.objects.filter(username=username).exists():
                    skipped_duplicate.append(username)
                    continue

                raw_password = row[password_idx] if password_idx is not None else None
                password = _cell_to_str(raw_password) or username

                message_limit = None
                if limit_idx is not None and row[limit_idx] not in (None, ""):
                    try:
                        message_limit = int(row[limit_idx])
                    except (TypeError, ValueError):
                        message_limit = None

                user = User(username=username, first_name=first_name, last_name=last_name)
                user.set_password(password)
                user.save()
                UserProfile.objects.create(user=user, message_limit=message_limit)

                created.append({"username": username, "password": password})
            except Exception as exc:
                # A problem with one row (e.g. a username too long, an
                # unexpected data type in a cell) no longer silently aborts
                # every row after it — it's recorded and the import
                # continues with the rest of the file.
                errors.append({"row": row_number, "detail": str(exc)})

        return Response(
            {
                "total_rows": len(data_rows),
                "created": created,
                "skipped_duplicate": skipped_duplicate,
                "skipped_blank_rows": skipped_blank,
                "errors": errors,
            },
            status=status.HTTP_201_CREATED,
        )


class AppSettingsView(generics.RetrieveUpdateAPIView):
    """
    Admin-only: GET/PATCH the org-wide settings (currently just
    daily_reset_time). Powers the Preferences tab.
    """

    serializer_class = AppSettingsSerializer
    permission_classes = [IsAdmin]

    def get_object(self):
        return AppSettings.load()
