'''A micro-asyncronous script derived from twisted.'''
import os

if os.environ.get('DJPCMS_ASYNCHRONOUS_FRAMEWORK') == 'twisted':
    from twisted.internet.defer import *
else:
    from pulsar.async.defer import *