import logging
import os
import sys

from djpcms import sites, MakeSite
from djpcms.test import TEST_TYPES
import djpcms.contrib as contrib
import examples
from djpcms.utils.importer import import_module

logger = logging.getLogger()

LIBRARY = 'djpcms'
CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
if CUR_DIR not in sys.path:
    sys.path.insert(0,CUR_DIR)
CONTRIB_DIR = os.path.dirname(contrib.__file__)
EXEMPLE_DIR = os.path.join(os.path.dirname(examples.__file__),'sitedjpcms')
sys.path.insert(0,EXEMPLE_DIR)


class exempledir:
    def __init__(self, d):
        self.d = d
    def __call__(self,test_type):
        return self.d
    
def all_test_dirs():
    yield lambda test_type : os.path.join(CUR_DIR,test_type)
    yield lambda test_type : CONTRIB_DIR
    for name in os.listdir(EXEMPLE_DIR):
        edir = os.path.join(EXEMPLE_DIR,name)
        if os.path.isdir(edir):
            yield exempledir(edir)
    
ALL_TEST_PATHS = tuple(all_test_dirs())

ALL_TEST_PATHS = (lambda test_type : os.path.join(CUR_DIR,test_type),
                  lambda test_type : CONTRIB_DIR,
                  lambda test_type : os.path.join(EXEMPLE_DIR,'exampleapps'))


def get_tests(test_type):
    for dirpath in ALL_TEST_PATHS:
        dirpath = dirpath(test_type)
        loc = os.path.split(dirpath)[1]
        for d in os.listdir(dirpath):
            if os.path.isdir(os.path.join(dirpath,d)):
                yield (loc,d)


def import_tests(tags, test_type, can_fail):
    model_labels = []
    INSTALLED_APPS = sites.settings.INSTALLED_APPS
    tried = 0
    for loc,app in get_tests(test_type):
        model_label = '{0}.{1}'.format(loc,app)
        if tags and app not in tags:
            logger.debug("Skipping model %s" % model_label)
            continue
        tried += 1
        logger.info("Importing model {0}".format(model_label))
        if loc == 'contrib':
            model_label = 'djpcms.'+model_label
        if model_label not in INSTALLED_APPS:
            if model_label in model_labels:
                raise ValueError('Application {0} already available in testsing'
                                 .format(model_label))
            model_labels.append(model_label)
            INSTALLED_APPS.append(model_label)
        else:
            raise ValueError('Application {0} already in INSTALLED_APPS.'
                             .format(model_label))
            
    if not tried:
        print('Could not find any tests. Aborting.')
        exit()
        
    # Now lets try to import the tests module them
    # Tests should be able to load even if dependencies are not met
    for model_label in model_labels:
        tests = model_label + '.tests'
        try:
            mod = import_module(tests)
        except ImportError as e:
            if can_fail:
                logger.warn("Could not import '%s'. %s" % (tests,e))
                continue
            raise
        yield mod

        
def run(tags = None, test_type = None,
        verbosity = 1, can_fail = True,
        show_list = False, config = None):
    '''Run tests'''
    test_type = test_type or 'regression'
    if test_type not in TEST_TYPES:
        print(('Unknown test type {0}. Must be one of {1}.'.format(test_type, ', '.join(TEST_TYPES))))
        exit()
    
    TestSuiteRunner = TEST_TYPES[test_type]
    if not TestSuiteRunner:
        print(('No test suite for {0}'.format(test_type)))
        exit()

    if show_list:
        n = 0
        for name in get_tests(test_type):
            n += 1
            print(("'{1}' (from {0})".format(*name)))
        print(('\nYou can run {0} different test labels'.format(n)))
    else:
        # Create the testing Site
        config = config or {}
        MakeSite(test_type,'conf',**config)
        modules = import_tests(tags, test_type, can_fail)
        runner  = TestSuiteRunner(verbosity = verbosity)
        runner.run_tests(modules)

