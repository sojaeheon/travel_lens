import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from travel.models import Country
from content.models import DestinationBlog, DestinationNews

BASE_DIR = Path("/data")


class Command(BaseCommand):
    help = "Load destination blog & news CSV data"

    @transaction.atomic
    def handle(self, *args, **options):
        self.load_blog()
        self.load_news()
        self.stdout.write(self.style.SUCCESS("✅ Content seed data loaded"))

    # -------------------------
    # Destination Blog
    # -------------------------
    def load_blog(self):
        if DestinationBlog.objects.exists():
            self.stdout.write("DestinationBlog already exists. Skip.")
            return

        path = BASE_DIR / "destination_blog.csv"
        objs = []

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    country = Country.objects.get(iso2=row["iso2"])
                except Country.DoesNotExist:
                    continue

                objs.append(
                    DestinationBlog(
                        country=country,
                        title=row["title"],
                        url=row["url"],
                        published_at=row["published_at"],
                    )
                )

        DestinationBlog.objects.bulk_create(objs, ignore_conflicts=True)

    # -------------------------
    # Destination News
    # -------------------------
    def load_news(self):
        if DestinationNews.objects.exists():
            self.stdout.write("DestinationNews already exists. Skip.")
            return

        path = BASE_DIR / "destination_news.csv"
        objs = []

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    country = Country.objects.get(iso2=row["iso2"])
                except Country.DoesNotExist:
                    continue

                objs.append(
                    DestinationNews(
                        country=country,
                        title=row["title"],
                        url=row["url"],
                        published_at=row["published_at"],
                    )
                )

        DestinationNews.objects.bulk_create(objs, ignore_conflicts=True)
