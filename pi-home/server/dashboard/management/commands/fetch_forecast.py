from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from dashboard.models import Forecast

# stub: replace with your real fetcher later
def fetch_from_provider(location: str):
    # return a list of dicts like the provider payload you need
    now = timezone.now()


class Command(BaseCommand):
    help = "Fetch weather forecast and upsert into DB"

    def add_arguments(self, parser):
        parser.add_argument("--location", required=True)

    def handle(self, *args, **opts):
        location = opts["location"]
        try:
            payload = fetch_from_provider(location)
        except Exception as e:
            raise CommandError(f"Fetch failed: {e}") from e

        upserts = 0
        for item in payload:
            obj, created = Forecast.objects.update_or_create(
                location=item["location"],
                at=item["at"],
                defaults=dict(
                    icon=item["icon"],
                    temperature_c=item["temperature_c"],
                    precip_prob=item["precip_prob"],
                    wind_bft=item["wind_bft"],
                ),
            )
            upserts += 1
        self.stdout.write(self.style.SUCCESS(f"Upserted {upserts} rows for {location}"))
