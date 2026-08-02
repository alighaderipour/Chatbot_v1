import uuid

from django.db import models


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "departments"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Section(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,  # deleting a department shouldn't wipe out its sections' history
        null=True,
        blank=True,
        related_name="sections",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sections"
        ordering = ["department__name", "name"]
        # Unique PER department, not globally — two different departments
        # having a section with the same name (e.g. both having an
        # "Administration" section) is completely normal in a real org.
        constraints = [
            models.UniqueConstraint(fields=["department", "name"], name="unique_section_per_department")
        ]

    def __str__(self):
        return f"{self.department}/{self.name}" if self.department else self.name


class PhoneType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)  # e.g. "Fax", "Station", "Direct line"
    is_mobile = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "phone_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class SectionPhone(models.Model):
    """
    A phone number that belongs to a section (an office/desk/fax line),
    not to a specific person — this is what lets someone's phone number
    "follow" automatically when they move sections: their phone isn't
    stored on their profile at all, it's looked up live via their current
    section.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="phones")
    phone_type = models.ForeignKey(PhoneType, on_delete=models.CASCADE, related_name="+")
    phone_number = models.CharField(max_length=30)

    class Meta:
        db_table = "section_phones"
        ordering = ["section", "phone_type"]

    def __str__(self):
        return f"{self.section} — {self.phone_type}: {self.phone_number}"
