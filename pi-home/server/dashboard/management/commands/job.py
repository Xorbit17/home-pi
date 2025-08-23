# dashboard/management/commands/hello.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Prints a greeting"

    def add_arguments(self, parser):
        # positional argument
        parser.add_argument("name", type=str)

        # optional flag
        parser.add_argument("--shout", action="store_true")

    def handle(self, *args, **options):
        name = options["name"]
        message = f"Hello, {name}!"
        if options["shout"]:
            message = message.upper()
        self.stdout.write(self.style.SUCCESS(message))
