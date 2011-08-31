from djpcms.apps.management.base import BaseCommand

class Command(BaseCommand):
    help = "Load the environment."
    
    def handle(self, callable, *args, **options):
        callable()