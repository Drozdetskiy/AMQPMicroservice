from django.core.management import BaseCommand, CommandError

from rating_consumer_service.rating_consumer import run_consumer


class Command(BaseCommand):
    help = 'Activate consumer script'

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.WARNING('Running consumer'))
            run_consumer()
        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR('Stop consumer'))
        except Exception:
            raise CommandError('Cant run consumer')
