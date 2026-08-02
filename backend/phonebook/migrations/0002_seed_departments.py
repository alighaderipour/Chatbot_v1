from django.db import migrations

# Extracted directly from your existing project's Departments.xlsx.
# One row was excluded: 'بـخش محل خدمـت' — that's a stray duplicate of the
# column header itself sitting in the data, not a real department.
DEPARTMENT_NAMES = [
    "زایشگاه", "دفتر پرستاری", "اتاق عمل", "آزمایشگاه", "درمان", "ICU",
    "داروخانه", "انتظامات", "جراحی مردان", "بهداشت", "کلینیک",
    "اورژانس برادران", "پذیرش (اطلاعات سلامت)", "درآمد", "دارو تجهیزات",
    "اورژانس خواهران", "بهبود کیفیت", "پشتیبانی", "فاوا",
    "حوزه نمایندگی و عقیدتی", "جراحی زنان", "CCU", "اطفال", "داخلی زنان",
    "داخلی مردان", "طرح و برنامه", "تصویر برداری", "اداری", "دفتر ریاست",
    "کمیسیون پزشکی", "نیروی انسانی", "نامشخص", "بازرسی",
    "اقدامات تامینی و حقوقی", "امداد عملیات و تربیت بدنی", "آموزش",
    "محوطه", "رادیولوژی", "ترابری",
]


def seed_departments(apps, schema_editor):
    Department = apps.get_model("phonebook", "Department")
    for name in DEPARTMENT_NAMES:
        Department.objects.get_or_create(name=name)


def remove_departments(apps, schema_editor):
    Department = apps.get_model("phonebook", "Department")
    Department.objects.filter(name__in=DEPARTMENT_NAMES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("phonebook", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_departments, remove_departments),
    ]
