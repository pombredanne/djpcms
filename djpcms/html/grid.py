from djpcms import to_string, UnicodeMixin
from djpcms.utils.const import EMPTY_VALUE

__all__ = ['get_cssgrid','EMPTY_VALUE','grid_systems','Grid960','Yui3']

grid_systems = [
                ('','-----------------------------'),
                ('960_12','960 grid 12 columns'),
                ('960_16','960 grid 16 columns'),
                ('960_12_float','960 grid 12 columns float'),
                ('960_16_float','960 grid 16 columns float'),
                ('yui3','Yui 3')
                ]


class CssGrid(UnicodeMixin):
    name = 'grid'
    def __init__(self, columns = None, fixed = None):
        self.empty = EMPTY_VALUE
        self.clear = ''
        self.container_class = ''
        self.column1 = ''
        self.setup(columns,fixed)
        
    def setup(self, columns, fixed):
        pass

    def __unicode__(self):
        if self.columns:
            na = '{0} {1}'.format(self.name,self.columns)
        else:
            na = self.name
        if not self.fixed:
            na += ' float'
        return to_string(na)
        
        
class Grid960(CssGrid):
    name = '960'
    def setup(self,columns,fixed):
        self.columns = columns if columns in (12,16) else 12
        self.fixed = fixed
        self.clear  = '<div class="clear"></div>'
        columns = self.columns
        c2 = columns//2
        c4 = columns//4
        c3 = 4 if columns == 12 else 5
        self.container_class = 'container_%s' % columns
        self.column1 = 'grid_%s' % columns
        self.column_1_2 = 'grid_{0}'.format(c2)
        #
        self.column_1_3 = 'grid_{0}'.format(c3)
        self.column_2_3 = 'grid_{0}'.format(2*c3)
        #
        self.column_1_4 = 'grid_{0}'.format(c4)
        self.column_3_4 = 'grid_{0}'.format(3*c4)
        #
        self.column_1_5 = 'grid_3'
        self.column_2_5 = 'grid_6'
        self.column_3_5 = 'grid_{0}'.format(columns-6)
        self.column_4_5 = 'grid_{0}'.format(columns-3)
        #
        self.column_1_6 = 'grid_2'
        self.column_5_6 = 'grid_{0}'.format(columns-2)
        
    

class Yui3(CssGrid):
    name = 'yui3'
    def setup(self,columns,fixed):
        self.columns = columns
        self.fixed = fixed
        columns = self.columns
        c4 = columns//4
        c6 = columns//6
        c3 = 2*c6
        self.container_class = 'yui3-g'
        self.column1 = 'yui3-u-1'
        self.column_1_2 = 'yui3-u-1-2'
        #
        self.column_1_3 = 'yui3-u-1-3'
        self.column_2_3 = 'yui3-u-2-3'
        #
        self.column_1_4 = 'yui3-u-1-4'
        self.column_3_4 = 'yui3-u-3-4'
        #
        self.column_1_5 = 'yui3-u-1-5'
        self.column_2_5 = 'yui3-u-2-5'
        self.column_3_5 = 'yui3-u-3-5'
        self.column_4_5 = 'yui3-u-4-5'
        #
        self.column_1_6 = 'yui3-u-1-6'
        self.column_5_6 = 'yui3-u-5-6'
    
def get_cssgrid(name):
    names = name.lower().split('_')
    name = names.pop(0)
    columns = None
    fixed = True
    for v in names:
        try:
            columns = int(v)
        except ValueError:
            if v == 'float':
                fixed = False
    if name == '960':
        return Grid960(columns,fixed)
    elif name == 'yui3':
        return Yui3(columns,fixed)
    elif name:
        raise ValueError('Grid "{0}" is not installed'.format(name))
    
    
        