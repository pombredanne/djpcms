'''I use this script to run tests on a windows development environment.
'''
import os
from djpcms.utils.pathtool import AddToPath

pt = AddToPath(__file__)
pt.add(module='pulsar', up = 1, down = ('pulsar',))
pt.add(module='stdnet', up = 1, down = ('python-stdnet',))
pt.add(module='djpapps', up = 1, down = ('djpapps',))
from runtests import suite

if __name__ == '__main__':
    suite().start()
    


 