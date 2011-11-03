'''\
Command to run tests for application built with djpcms
'''
import os
from optparse import make_option

from djpcms.utils.importer import import_module
from djpcms.apps.management.base import BaseCommand
from djpcms.test import TEST_TYPES


def get_tests(loc):
    for d in os.listdir(loc):
        df = os.path.join(loc,d)
        dd = d.split('.')
        if d.startswith('_') or d.startswith('.') or len(dd) > 2:
            continue
        if (os.path.isdir(df) and len(dd)>1) or\
           (os.path.isfile(df) and dd[1]!='py'):
            continue
        yield dd[0]

                
def import_tests(tags,loc,test_module):
    for t in get_tests(loc):
        if tags and t not in tags:
            continue
        yield import_module('{0}.{1}'.format(test_module,t))


def runtests(sites, tags, test_type, verbosity):
    if test_type not in TEST_TYPES:
        print(('Unknown test type {0}. Must be one of {1}.'.format(test_type, ', '.join(TEST_TYPES))))
        return
    TestSuiteRunner = TEST_TYPES[test_type]
    loc = sites.settings.SITE_DIRECTORY
    test_loc = os.path.join(loc,'tests',test_type)
    if os.path.exists(test_loc):
        test_module = '{0}.{1}.{2}'.format(sites.settings.SITE_MODULE,'tests',test_type)
        modules = import_tests(tags,test_loc,test_module)
        runner  = TestSuiteRunner(verbosity = verbosity)
        runner.run_tests(modules)
    else:
        print(('No tests. Directory {0} not available.'.format(test_loc)))


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-t", "--type",
                    action="store",
                    dest="test_type",
                    default='regression',
                    help='Test type, possible choices are:\
 regression (default)\
 bench\
 profile'),
        make_option("-d", "--database",
                    action="store_true",
                    dest="database",
                    default=False,
                    help='use production database settings'),
        make_option("-s", "--settings",
                    action="store",
                    dest="test_settings",
                    default='test_settings',
                    help='Specify the test settings module which overrides \
 the production settings. Default Value "test_settings"')
    )
    help = "Test a djpcms application."
    args = '[testname1 testname2 ...]'
    
    def handle(self, sites, *args, **options):
        if not sites:
            print('No sites installed, cannot test the application')
        else:
            if not options['database']:
                sites.settings.DATABASES = \
                {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
            test_type = options['test_type']
            # We now load the sites
            sites.setsettings(DEBUG = False)
            #
            # We need to import the settings file for testing
            sites.loadsettings(options['test_settings'])
            sites.load()
            runtests(sites,args,test_type,options['verbosity'])

    