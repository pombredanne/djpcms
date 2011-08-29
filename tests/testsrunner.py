import logging
import os
import sys

from djpcms import sites, LIBRARY_NAME
from djpcms.test import TEST_TYPES, TestDirectory,\
                        ContribTestDirectory, SiteTestDirectory,\
                        setup_logging
import djpcms.contrib as contrib
from djpcms.utils.structures import OrderedDict
from djpcms.utils.importer import import_module

import examples

logger = logging.getLogger()

CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
ALL_TESTS = (TestDirectory(CUR_DIR),
             ContribTestDirectory(LIBRARY_NAME,'contrib'))


def get_tests(test_type):
    for t in ALL_TESTS:
        dirpath = t.dirpath(test_type)
        for d in os.listdir(dirpath):
            if not d.startswith('__') and os.path.isdir(os.path.join(dirpath,d)):
                yield (t,d)


def import_tests(tags, test_type, can_fail):
    model_labels = OrderedDict()
    INSTALLED_APPS = sites.settings.INSTALLED_APPS
    applications = []
    for t,app in get_tests(test_type):
        model_app = t.app_label(test_type,app)
        if tags and app not in tags:
            continue
        try:
            import_module(model_app)
        except ImportError:
            logger.error("Error importing module {0}.".format(model_app),
                         exc_info = sys.exc_info())
            continue
        logger.debug("Importing model {0}".format(model_app))
        model_labels[model_app] = t
        if model_app not in INSTALLED_APPS: 
            INSTALLED_APPS.append(model_app)
        applications.append(model_app)
    
    for app in INSTALLED_APPS:
        if app == 'djpcms' or app.startswith('djpcms.') or app in applications:  
            continue
        if tags and app not in tags:
            continue
        model_labels[app] = ContribTestDirectory(app)
        
    if not model_labels:
        print('Could not find any tests. Aborting.')
        exit()
        
    # Now lets try to import the tests module them
    # Tests should be able to load even if dependencies are not met
    for model_label,t in model_labels.items():
        tests = t.test_module(test_type,model_label)
        try:
            mod = import_module(tests)
        except ImportError as e:
            logger.warn("Could not import '%s'. %s" % (tests,e))
            continue
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
        CMS_ORM = config.get('CMS_ORM', '')
        if CMS_ORM:
            conf = 'conf_' + CMS_ORM
        else:
            conf = 'conf'
          
        testsite = sites.make(test_type,
                              conf,
                              **config)
        setup_logging(verbosity)
        sites.load()
        
        sites.tests = testsite.settings
        modules = import_tests(tags, test_type, can_fail)
        runner  = TestSuiteRunner(verbosity = verbosity)
        runner.run_tests(modules)

