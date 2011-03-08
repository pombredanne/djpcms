#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

import djpcms


def makeoptions():
    parser = OptionParser()
    parser.add_option("-v", "--verbosity",
                      type = int,
                      action="store",
                      dest="verbosity",
                      default=1,
                      help="Tests verbosity level, one of 0, 1, 2 or 3")
    parser.add_option("-l", "--list",
                      action="store_true",
                      dest="show_list",
                      default=False,
                      help="Show the list of available test labels for a given test type")
    parser.add_option("-f", "--skipfail",
                      action="store_false",
                      dest="can_fail",
                      default=False,
                      help="If set, the tests will run even if there is an import error in tests")
    parser.add_option("-m", "--model",
                      action="store",
                      dest="model",
                      default='django',
                      help="The object relational mapper to use. One of django, stdnet (default django)")
    parser.add_option('-p', '--template',
                      action="store",
                      dest="template",
                      default='django',
                      help="Template library to use. One of django or jinja2 (default django).")
    parser.add_option('-g', '--httplib',
                      action="store",
                      dest="httplib",
                      default='django',
                      help="HTTP library to use One of django or werkzeug (default django).")
    parser.add_option("-t", "--type",
                      action="store",
                      dest="test_type",
                      default='regression',
                      help="Test type, possible choices are:\
 regression (default)\
 bench\
 profile")
    return parser


def addpath():
    # add this directory to the Python Path so that tests and examples are visible
    p = os.path
    path = p.split(p.abspath(__file__))[0]
    if path not in sys.path:
        sys.path.insert(0, path)
    path = p.join(path,'tests')
    if path not in sys.path:
        sys.path.insert(0, path)
    
addpath()


def run():
    options, tags = makeoptions().parse_args()
    from testsrunner import run
    config = {'CMS_ORM':options.model,
              'TEMPLATE_ENGINE':options.template,
              'HTTP_LIBRARY':options.httplib}
    run(tags,
        test_type = options.test_type,
        can_fail=options.can_fail,
        verbosity=options.verbosity,
        show_list=options.show_list,
        config = config)
    

if __name__ == '__main__':
    run()
    