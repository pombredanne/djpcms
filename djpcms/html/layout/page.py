'''Page layout and grids
'''
from djpcms.html import WidgetMaker

__all__ = ['LayoutDoesNotExist',
           'grid_systems',
           'grid',
           'grids',
           'elem',
           'page',
           'container',
           'Grid',
           'row',
           'column']


grid_systems = [
                ('fixed_12','Fixed grid 12 columns'),
                ('fixed_24','Fixed grid 24 columns'),
                ('float_12','Float grid 12 columns'),
                ('float_24','Float grid 24 columns'),
                ]

_grid_layouts = {}


class LayoutDoesNotExist(Exception):
    pass


def grids():
    return sorted(_grid_layouts)

def grid(name):
    try:
        return _grid_layouts[name.lower()]
    except KeyError:
        raise LayoutDoesNotExist(name)


class CssGrid(object):
    
    def __init__(self, columns = 12, fixed = True):
        self.columns = columns
        self.fixed = bool(fixed)
        
    def add_css_data(self, widget):
        maker = widget.maker
        if isinstance(maker,row):
            if isinstance(maker.parent, container) and self.fixed:
                widget.addClass('row_{0}'.format(self.columns))
            else:
                widget.addClass('row-fluid_{0}'.format(self.columns))
        elif isinstance(maker, column):
            span = maker.size * self.columns // maker.over
            widget.addClass('span{0}'.format(span))
    

class elem(WidgetMaker):
    '''A page layout contains all the information for rendering and styling a
web page'''
    tag = 'div'
    role = None
    
    def __init__(self, *children, **kwargs):
        role = kwargs.pop('role',self.role)
        if role:
            data = kwargs.get('data',{})
            data['role'] = role
            kwargs['data'] = data
        super(elem, self).__init__(**kwargs)
        self.add(*children)
    
    @property
    def numblocks(self):
        return len(tuple(self.blocks()))
    
    def is_block(self):
        return False
    
    def blocks(self):
        '''Generator of blocks.'''
        # loop over children
        for child in self.allchildren:
            for block in child.blocks():
                yield block
    
    def block_dictionary(self):
        return dict(((n,block) for n,block in enumerate(self.blocks())))
                
    def add(self, *widgets):
        child_type = self.childtype()
        for w in widgets:
            if not isinstance(w, child_type):
                raise ValueError('"{0}" cannot be a child of "{1}".'\
                                 .format(w, self))
        return super(elem, self).add(*widgets)
    
    @classmethod
    def childtype(cls):
        return WidgetMaker 

    def render_from_widget(self, request, widget, context):
        #grid = request.cssgrid()
        grid = CssGrid()
        grid.add_css_data(widget)
        return super(elem,self).render_from_widget(
                               request, widget, context)
        

class container(elem):
    '''This act as a container for its children. It does not render
to anything'''
    def __init__(self, key, *children, **kwargs):
        kwargs['key'] = key
        super(container,self).__init__(*children, **kwargs)
        

class page(elem):
    '''layout for a page'''
    columns = 12
    role = 'page'
    
    def __init__(self, *containers, **kwargs):
        self.columns = kwargs.pop('columns', self.columns)
        if not containers:
            containers = (container('content'),)
        super(page, self).__init__(*containers, **kwargs)
    
    
class Grid(elem):
    '''A grid element is the container of rows.'''
    default_class = 'grid-container'
    
    def __init__(self, *rows, **kwargs):
        cleaned_rows = []
        for row in rows:
            if isinstance(row,Grid):
                cleaned_rows.extend(row.allchildren)
            else:
                cleaned_rows.append(row)
        super(Grid, self).__init__(*cleaned_rows, **kwargs)
        
    @classmethod
    def childtype(cls):
        return row
    
    def register(self, name):
        name = name.lower()
        _grid_layouts[name] = self
        return self
    
    
class column(elem):
    '''A column is a special container. It is the container which holds djpcms
plugins, unless it has children containers.'''
    default_class = None
    def __init__(self, size = 1, over = 1, *grid, **kwargs):
        self.size = size
        self.over = over
        if self.span > 1:
            raise ValueError('Column span "{0}" is greater than one!'\
                             .format(self.span))
        if len(grid) > 1:
            raise RunTimeError('Only one grid can be passed to column')
        super(column, self).__init__(*grid, **kwargs)
        
    @property
    def span(self):
        return float(self.size)/self.over
    
    @classmethod
    def childtype(cls):
        return Grid
    
    def is_block(self):
        return not bool(self.allchildren)
    
    def blocks(self):
        '''Override the blocks generator since column si special. If there are
no children, it return self as the only child.'''
        if not self.allchildren:
            yield self
        else:
            for child in super(column,self).blocks():
                yield child
        
        
class row(elem):
    
    def __init__(self, *columns, **kwargs):
        if not columns:
            columns = (column(),)
        super(row, self).__init__(*columns, **kwargs)
        
    @classmethod
    def childtype(cls):
        return column
    
    
class tabs(row):
    
    def __init__(self, *columns, **kwargs):
        if not columns:
            columns = (column(),)
        super(row, self).__init__(*columns, **kwargs)
        

# Simple grids registration
Grid(
    row()
).register('grid 100')

Grid(
    row(column(1,2), column(1,2))
).register('grid 50-50')

Grid(
    row(column(1,3), column(1,3), column(1,3))
).register('grid 33-33-33')

Grid(
    row(column(1,4), column(1,4), column(1,4), column(1,4))
).register('grid 25-25-25-25')

Grid(
    row(column(1,3), column(2,3))
).register('grid 33-66')

Grid(
    row(column(2,3), column(1,3))
).register('grid 66-33')

Grid(
    row(column(1,4), column(3,4))
).register('grid 25-75')

Grid(
    row(column(3,4), column(1,4))
).register('grid 75-25')
