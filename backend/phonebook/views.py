from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Department, PhoneType, Section, SectionPhone
from .permissions import IsAdminOrReadOnly
from .serializers import (
    DepartmentSerializer,
    PersonSearchResultSerializer,
    PhoneTypeSerializer,
    SectionPhoneSerializer,
    SectionSearchResultSerializer,
    SectionSerializer,
)


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]


class SectionListCreateView(generics.ListCreateAPIView):
    serializer_class = SectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Section.objects.select_related("department").prefetch_related("phones__phone_type")
        department_id = self.request.query_params.get("department")
        if department_id:
            qs = qs.filter(department_id=department_id)
        return qs


class SectionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAdminOrReadOnly]


class PhoneTypeListCreateView(generics.ListCreateAPIView):
    queryset = PhoneType.objects.all()
    serializer_class = PhoneTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


class PhoneTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PhoneType.objects.all()
    serializer_class = PhoneTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


class SectionPhoneListCreateView(generics.ListCreateAPIView):
    serializer_class = SectionPhoneSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = SectionPhone.objects.select_related("phone_type", "section")
        section_id = self.request.query_params.get("section")
        if section_id:
            qs = qs.filter(section_id=section_id)
        return qs


class SectionPhoneDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SectionPhone.objects.all()
    serializer_class = SectionPhoneSerializer
    permission_classes = [IsAdminOrReadOnly]


class SearchView(APIView):
    """
    GET /api/phonebook/search/?q=...

    Any authenticated user (this is the read-only search regular users get).
    Matches people by name/username/department/section, and sections by
    name/department — covers both "find a person" and "find a department's
    phone number" in one box.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"people": [], "sections": []})

        users = (
            User.objects.filter(is_active=True)
            .filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(username__icontains=query)
                | Q(profile__department__name__icontains=query)
                | Q(profile__section__name__icontains=query)
            )
            .select_related("profile", "profile__department", "profile__section")
            .prefetch_related("profile__section__phones__phone_type")
            .distinct()[:50]
        )

        people = []
        for user in users:
            profile = getattr(user, "profile", None)
            section = profile.section if profile else None
            people.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "department_name": profile.department.name if profile and profile.department else None,
                    "section_name": section.name if section else None,
                    "personal_phone": profile.personal_phone if profile else None,
                    "section_phones": section.phones.all() if section else [],
                }
            )

        sections = (
            Section.objects.filter(Q(name__icontains=query) | Q(department__name__icontains=query))
            .select_related("department")
            .prefetch_related("phones__phone_type")
            .distinct()[:50]
        )

        return Response(
            {
                "people": PersonSearchResultSerializer(people, many=True).data,
                "sections": SectionSearchResultSerializer(sections, many=True).data,
            }
        )
