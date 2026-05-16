import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from content.models import Experience, Category, Location


class Command(BaseCommand):
    help = "Import places with foreign keys"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs["csv_file"]

        categories = {c.name.strip().lower(): c for c in Category.objects.all()}

        locations = {l.name.strip().lower(): l for l in Location.objects.all()}

        created_count = 0

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            self.stdout.write(self.style.WARNING(f"Headers: {reader.fieldnames}"))

            for row in reader:
                try:
                    cat_name = row["CATEGORY"].strip()
                    cat_key = cat_name.lower()
                    # self.stdout.write(self.style.SUCCESS(f"{cat_name}"))
                    category = categories.get(cat_key)
                    # self.stdout.write(self.style.WARNING(f"{categories}"))
                    if not category:
                        category = Category.objects.create(name=cat_name)
                        categories[cat_name] = category

                    loc_name = row["LOCATION"].strip()
                    loc_key = loc_name.lower()

                    location = locations.get(loc_key)
                    if not location:
                        location = Location.objects.create(name=loc_name)
                        locations[loc_key] = location

                    is_open = row["IS_OPEN"].strip().lower() in ["TRUE", "1", "yes"]

                    opening_time = datetime.strptime(
                        row["OPENING_TIME"], "%H:%M:%S"
                    ).time()
                    closing_time = datetime.strptime(
                        row["CLOSING_TIME"], "%H:%M:%S"
                    ).time()
                    last_entry_time = datetime.strptime(
                        row["LAST_ENTRY_TIME"], "%H:%M:%S"
                    ).time()

                    place = Experience(
                        name=row["NAME"],
                        description=row["DESCRIPTION"],
                        location=location,  # 🔑 FK
                        latitude=float(row["LATITUDE"]),
                        longitude=float(row["LONGITUDE"]),
                        image_url=row["IMAGE_URL"],
                        max_daily_capacity=int(row["MAX_DAILY_CAPACITY"]),
                        entry_fee_base=float(row["ENTRY_FEE_BASE"]),
                        is_open=is_open,
                        opening_time=opening_time,
                        closing_time=closing_time,
                        last_entry_time=last_entry_time,
                        category=category,  # 🔑 FK
                        deleted_at=None,
                    )

                    place.save()
                    created_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping row: {row} | Error: {e}")
                    )

        self.stdout.write(
            self.style.SUCCESS(f"Imported {created_count} places successfully!")
        )
