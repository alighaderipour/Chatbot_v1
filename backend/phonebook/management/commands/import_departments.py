import csv

from django.core.management.base import BaseCommand, CommandError

from phonebook.models import Department


class Command(BaseCommand):
    help = (
        "Import departments from a CSV file (expects a 'name' column, and "
        "optionally a 'description' column). Export your existing "
        "departments table from the old phonebook project to CSV first — "
        "e.g. in phpMyAdmin/MySQL Workbench: Export > CSV."
    )

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):
        path = options["csv_path"]
        try:
            f = open(path, newline="", encoding="utf-8-sig")
        except OSError as exc:
            raise CommandError(f"Could not open {path}: {exc}")

        with f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None or "name" not in [
                (h or "").strip().lower() for h in reader.fieldnames
            ]:
                raise CommandError("CSV must have a 'name' column.")

            created, skipped = 0, 0
            for row in reader:
                name = (row.get("name") or row.get("department_name") or "").strip()
                if not name:
                    continue
                description = (row.get("description") or "").strip() or None
                _, was_created = Department.objects.get_or_create(
                    name=name, defaults={"description": description}
                )
                created += was_created
                skipped += not was_created

        self.stdout.write(self.style.SUCCESS(f"Created {created} department(s), skipped {skipped} existing."))
