import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.db import transaction
from travel.models import Country, Currency, Airport, TravelAlert

BASE_DIR = Path("/data")


class Command(BaseCommand):
    help = "Load travel seed data (country, currency)"

    @transaction.atomic
    def handle(self, *args, **options):

        self.load_country()
        self.load_currency()
        # self.load_airport()
        # self.load_travel_alert()

        self.stdout.write(self.style.SUCCESS("✅ Travel seed data loaded"))

    # -----------------------
    # 1. Country
    # -----------------------
    def load_country(self):
        if Country.objects.exists():
            self.stdout.write("Country already exists. Skip.")
            return

        path = BASE_DIR / "country.csv"
        objs = []

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                objs.append(
                    Country(
                        iso2=row["iso2"],
                        iso3=row["iso3"],
                        name_ko=row["name_ko"],
                        name_en=row["name_en"],
                        continent_name_en=row["continent_name_en"],
                        continent_name_ko=row["continent_name_ko"],
                    )
                )

        Country.objects.bulk_create(objs)

    # -----------------------
    # 2. Currency
    # -----------------------
    def load_currency(self):
        if Currency.objects.exists():
            self.stdout.write("Currency already exists. Skip.")
            return

        path = BASE_DIR / "currency.csv"
        objs = []

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    country = Country.objects.get(iso2=row["iso2"])
                except Country.DoesNotExist:
                    continue

                objs.append(
                    Currency(
                        country=country,
                        currency_unit_ko=row["currency_unit_ko"],
                        currency_code=row["currency_code"],
                        currency_trunc_unit=int(row["currency_trunc_unit"]),
                        currency_krw_unit=row["currency_krw_unit"] or None,
                        updated_at=row["recorded_date"] or None,
                    )
                )

        Currency.objects.bulk_create(objs)

    # # -----------------------
    # # 3. Airport
    # # -----------------------
    # def load_airport(self):
    #     if Airport.objects.exists():
    #         self.stdout.write("Airport already exists. Skip.")
    #         return

    #     path = BASE_DIR / "airport.csv"
    #     objs = []

    #     with open(path, encoding="utf-8") as f:
    #         reader = csv.DictReader(f)
    #         for row in reader:
    #             try:
    #                 country = Country.objects.get(iso2=row["iso2"])
    #             except Country.DoesNotExist:
    #                 continue

    #             objs.append(
    #                 Airport(
    #                     country=country,
    #                     airport_name_ko=row["airport_name_ko"],
    #                     airport_code_iata=row["airport_code_iata"],
    #                     flight_price=row["flight_price"] or None,
    #                 )
    #             )

    #     Airport.objects.bulk_create(objs)

    # # -----------------------
    # # 4. Travel Alert
    # # -----------------------
    # def load_travel_alert(self):
    #     if TravelAlert.objects.exists():
    #         self.stdout.write("TravelAlert already exists. Skip.")
    #         return

    #     path = BASE_DIR / "travel_alert.csv"
    #     objs = []

    #     with open(path, encoding="utf-8") as f:
    #         reader = csv.DictReader(f)
    #         for row in reader:
    #             try:
    #                 country = Country.objects.get(iso2=row["iso2"])
    #             except Country.DoesNotExist:
    #                 continue

    #             objs.append(
    #                 TravelAlert(
    #                     country=country,
    #                     alarm_level=row["alarm_level"],
    #                     region=row["region"],
    #                     updated_at=row["updated_at"] or None,
    #                 )
    #             )

    #     TravelAlert.objects.bulk_create(objs)
