from django.core.management.base import BaseCommand

from phonebook.models import Department, Section


class Command(BaseCommand):
    help = (
        "Creates one Section per existing Department, named the same as "
        "the department, for any department that doesn't already have at "
        "least one section. Safe to run more than once — a department "
        "with a section already isn't touched. Use this as a starting "
        "point, then split departments into real sections manually "
        "through the admin Phonebook screens whenever you're ready."
    )

    def handle(self, *args, **options):
        created = 0
        for department in Department.objects.all():
            if department.sections.exists():
                continue
            Section.objects.create(department=department, name=department.name)
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} section(s)."))
