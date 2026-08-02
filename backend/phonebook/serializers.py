from rest_framework import serializers

from .models import Department, PhoneType, Section, SectionPhone


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description", "is_active"]


class PhoneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneType
        fields = ["id", "name", "is_mobile", "is_active"]


class SectionPhoneSerializer(serializers.ModelSerializer):
    phone_type_name = serializers.CharField(source="phone_type.name", read_only=True)

    class Meta:
        model = SectionPhone
        fields = ["id", "section", "phone_type", "phone_type_name", "phone_number"]


class SectionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source="department.name", read_only=True)
    phones = SectionPhoneSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "department", "department_name", "name", "description", "is_active", "phones"]


class SectionSearchResultSerializer(serializers.ModelSerializer):
    """Lighter-weight shape used in search results (no description/is_active noise)."""

    department_name = serializers.CharField(source="department.name", read_only=True)
    phones = SectionPhoneSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "name", "department_name", "phones"]


class PersonSearchResultSerializer(serializers.Serializer):
    """
    Built manually from a User in views.py rather than being a ModelSerializer
    on User — deliberately excludes national_id (sensitive) and anything
    account-related (is_staff, etc.) since this is what any logged-in
    coworker sees when searching, not an admin view.
    """

    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    department_name = serializers.CharField(allow_null=True)
    section_name = serializers.CharField(allow_null=True)
    personal_phone = serializers.CharField(allow_null=True)
    section_phones = SectionPhoneSerializer(many=True)
