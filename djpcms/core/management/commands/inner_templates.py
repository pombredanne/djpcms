import logging

import djpcms
from djpcms.html.template import make_default_inners

logger = logging.getLogger('djpcms.execute.inner_templates')


class Command(djpcms.Command):
    help = "Add default inner templates to the database."
    
    def handle(self, site_factory, options):
        logger.info('Adding default inner templates to database.')
        sites = site_factory()
        inners = make_default_inners(sites)
        for a in inners:
            logger.info('Added {0}'.format(a))
        
        logger.info('Added {0} templates to database.'.format(len(inners)))