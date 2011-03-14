'''\
Utility for managing grid 960 css templates
'''
from py2py3 import to_string

from djpcms.utils.const import EMPTY_VALUE

__all__ = ['grid960','EMPTY_VALUE','CLEAR_GRID']

CLEAR_GRID = to_string('<div class="clear"></div>')


def grid960(columns = None, fixed = True):        
    if columns == 16:
        return grid960_16(fixed)
    else:
        return grid960_12(fixed)


class grid960_base(object):
    '''
    960 grid layout container
    '''
    def __init__(self, columns, fixed):
        self.fixed  = fixed
        self.clear  = CLEAR_GRID
        self.empty  = EMPTY_VALUE
        c4 = columns//4
        c6 = columns//6
        c3 = 2*c6
        self.container_class = 'container_%s' % columns
        self.column1 = 'grid_%s' % columns
        self.column_1_2 = 'grid_%s' % (2*c4,)
        self.column_3_4 = 'grid_%s' % (3*c4,)
        self.column_1_4 = 'grid_%s' % c4
        self.column_1_3 = 'grid_%s' % c3
        self.column_1_6 = 'grid_%s' % c6
        self.column_2_3 = 'grid_%s' % (2*c3,)
        self.column_5_6 = 'grid_%s' % (5*c6,)


class grid960_12(grid960_base):
    '''
    960 grid layout container
    '''
    def __init__(self, fixed):
        super(grid960_12,self).__init__(12,fixed)
        
        
        
class grid960_16(grid960_base):
    
    def __init__(self,fixed):
        super(grid960_16,self).__init__(16,fixed)
