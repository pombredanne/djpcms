import logging

from djpcms.apps.management.base import BaseCommand
from djpcms.template import make_default_inners

logger = logging.getLogger('djpcms.execute.inner_templates')


class Command(BaseCommand):
    help = "Add default inner templates to the database."
    
    def handle(self, callable, *args, **options):
        logger.info('Adding default inner templates to database.')
        sites = callable()
        inners = make_default_inners()
        for a in inners:
            logger.info('Added {0}'.format(a))
        
        logger.info('Added {0} templates to database.'.format(len(inners)))