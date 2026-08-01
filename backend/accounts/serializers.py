from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AppSettings, UserProfile


class UserSerializer(serializers.ModelSerializer):
    """Used for listing users and for GET on a single user — the FULL
    representation. Also used to build PATCH responses (see views.py),
    since UserUpdateSerializer alone only outputs the fields it accepts as
    input, which isn't enough for the frontend to keep its list in sync."""

    message_limit = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()

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
        ]
        read_only_fields = ["id", "username", "date_joined", "message_count"]

    def get_message_limit(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile.message_limit

    def get_message_count(self, obj):
        profile, _ = UserProfile.objects.get_or_create(user=obj)
        return profile.message_count


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=1)
    message_limit = serializers.IntegerField(required=False, allow_null=True, default=None)

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
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        message_limit = validated_data.pop("message_limit", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, message_limit=message_limit)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """PATCH input only — deliberately narrow (see views.py, which
    re-serializes the response with the full UserSerializer instead of
    returning this serializer's own limited output)."""

    message_limit = serializers.IntegerField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

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
        ]

    def update(self, instance, validated_data):
        message_limit = validated_data.pop("message_limit", serializers.empty)
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

        if message_limit is not serializers.empty:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            profile.message_limit = message_limit
            profile.save(update_fields=["message_limit"])

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
