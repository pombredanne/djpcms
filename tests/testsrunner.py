import logging
import os
import sys

from djpcms import sites, LIBRARY_NAME
from djpcms.test import TEST_TYPES, TestDirectory,\
                        ContribTestDirectory, SiteTestDirectory
import djpcms.contrib as contrib
from djpcms.utils.collections import OrderedDict
from djpcms.utils.importer import import_module
import examples

logger = logging.getLogger()

CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
#if CUR_DIR not in sys.path:
#    sys.path.insert(0,CUR_DIR)
#EXEMPLE_DIR = os.path.join(os.path.dirname(examples.__file__),'sitedjpcms')
#sys.path.insert(0,EXEMPLE_DIR)
#ALL_TEST_PATHS = (TestDirectory(CUR_DIR),
#                  ContribTestDirectory(CONTRIB_DIR),
#                  ExampleTestDirectory(os.path.join(EXEMPLE_DIR,'exampleapps'))
ALL_TESTS = (TestDirectory(CUR_DIR),
             ContribTestDirectory(LIBRARY_NAME,'contrib'))


def get_tests(test_type):
    for t in ALL_TESTS:
        dirpath = t.dirpath(test_type)
        for d in os.listdir(dirpath):
            if os.path.isdir(os.path.join(dirpath,d)):
                yield (t,d)


def import_tests(tags, test_type, can_fail):
    model_labels = OrderedDict()
    model_labels_all = OrderedDict()
    INSTALLED_APPS = sites.settings.INSTALLED_APPS
    tried = 0
    for t,app in get_tests(test_type):
        model_app = t.app_label(test_type,app)
        if tags and app not in tags:
            logger.debug("Skipping model %s" % model_app)
            continue
        tried += 1
        logger.info("Importing model {0}".format(model_app))
        first = True
        for model_label in t.all_model_labels(test_type,app):
            if model_label not in INSTALLED_APPS:
                if model_label in model_labels_all:
                    raise ValueError('Application {0} already available in testsing'
                                     .format(model_label))
            else:
                raise ValueError('Application {0} already in INSTALLED_APPS.'
                             .format(model_label))
            model_labels_all[model_label] = t
            if first:
                first = False
                model_labels[model_label] = t
            INSTALLED_APPS.append(model_label)
            
    if not tried:
        print('Could not find any tests. Aborting.')
        exit()
        
    # Now lets try to import the tests module them
    # Tests should be able to load even if dependencies are not met
    for model_label,t in model_labels.items():
        tests = t.test_module(test_type,model_label)
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
        testsite = sites.make(test_type,'conf',**config)
        # Inject the test settings to sites global variable
        sites.tests = testsite.settings 
        modules = import_tests(tags, test_type, can_fail)
        runner  = TestSuiteRunner(verbosity = verbosity)
        runner.run_tests(modules)

