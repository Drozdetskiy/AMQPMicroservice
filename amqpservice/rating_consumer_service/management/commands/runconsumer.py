from django.conf import settings
from django.core.management import BaseCommand, CommandError

from rating_consumer_service.rating_consumer import run_consumer


class Command(BaseCommand):
    help = 'Activate consumer script'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Running consumer...'))

        if not settings.configured:
            settings.configure(**locals())

        try:
            run_consumer()
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR('Stop consumer'))
        except Exception as e:
            raise CommandError('Cant run consumer because: ', e)
