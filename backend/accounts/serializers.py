from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AppSettings, UserProfile
from phonebook.models import Department, Section


class UserSerializer(serializers.ModelSerializer):
    """Used for listing users and for GET on a single user — the FULL
    representation. Also used to build PATCH responses (see views.py),
    since UserUpdateSerializer alone only outputs the fields it accepts as
    input, which isn't enough for the frontend to keep its list in sync."""

    message_limit = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    national_id = serializers.SerializerMethodField()
    personal_phone = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "message_limit",
            "message_count",
            "national_id",
            "personal_phone",
            "department",
            "section",
        ]
        read_only_fields = ["id", "username", "date_joined", "message_count"]

    def _profile(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile

    def get_message_limit(self, obj):
        return self._profile(obj).message_limit

    def get_message_count(self, obj):
        return self._profile(obj).message_count

    def get_national_id(self, obj):
        return self._profile(obj).national_id

    def get_personal_phone(self, obj):
        return self._profile(obj).personal_phone

    def get_department(self, obj):
        dept = self._profile(obj).department
        return {"id": dept.id, "name": dept.name} if dept else None

    def get_section(self, obj):
        section = self._profile(obj).section
        return {"id": section.id, "name": section.name} if section else None


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=1)
    message_limit = serializers.IntegerField(required=False, allow_null=True, default=None)
    national_id = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    personal_phone = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True, default=None
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), required=False, allow_null=True, default=None
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
            "is_staff",
            "is_superuser",
            "message_limit",
            "national_id",
            "personal_phone",
            "department",
            "section",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        profile_fields = {
            "message_limit": validated_data.pop("message_limit", None),
            "national_id": validated_data.pop("national_id", None) or None,
            "personal_phone": validated_data.pop("personal_phone", None) or None,
            "department": validated_data.pop("department", None),
            "section": validated_data.pop("section", None),
        }
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_fields)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """PATCH input only — deliberately narrow (see views.py, which
    re-serializes the response with the full UserSerializer instead of
    returning this serializer's own limited output)."""

    message_limit = serializers.IntegerField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    national_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    personal_phone = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), required=False, allow_null=True
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "message_limit",
            "password",
            "national_id",
            "personal_phone",
            "department",
            "section",
        ]

    def update(self, instance, validated_data):
        profile_updates = {}
        for field in ("message_limit", "national_id", "personal_phone", "department", "section"):
            if field in validated_data:
                profile_updates[field] = validated_data.pop(field)

        password = validated_data.pop("password", None)

        # Blank name fields mean "leave unchanged" — the frontend
        # intentionally leaves these empty in the edit form (rather than
        # pre-filling the current name) so a blank submission can't
        # accidentally overwrite a name with an empty string.
        for field in ("first_name", "last_name"):
            if field in validated_data and not validated_data[field]:
                validated_data.pop(field)

        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])

        if profile_updates:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for field, value in profile_updates.items():
                # Blank string (not None) for national_id/personal_phone
                # also means "leave unchanged", same reasoning as names above.
                if field in ("national_id", "personal_phone") and value == "":
                    continue
                setattr(profile, field, value)
            profile.save()

        return instance


class MeSerializer(serializers.ModelSerializer):
    """What the frontend fetches after login to know the current user's own
    role tier and message usage."""

    message_limit = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
            "message_limit",
            "message_count",
        ]

    def get_message_limit(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile.message_limit

    def get_message_count(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile.message_count


class AppSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSettings
        fields = ["daily_reset_time", "last_reset_date"]
        read_only_fields = ["last_reset_date"]
