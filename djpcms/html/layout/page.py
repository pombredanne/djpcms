'''Page layout and grids
'''
from djpcms.html import WidgetMaker

__all__ = ['LayoutDoesNotExist',
           'get_layout',
           'get_grid',
           'page_layouts',
           'elem',
           'page',
           'container',
           'grid',
           'row',
           'column']


_page_layouts = {'page': {},
                 'grid': {}}


class LayoutDoesNotExist(Exception):
    pass


def page_layouts(grid = False):
    if grid:
        return sorted(_page_layouts['grid'])
    else:
        return sorted(_page_layouts['page'])

def get_layout(name, grid = False):
    pages = _page_layouts['grid' if grid else 'page']
    try:
        return pages[name.lower()]
    except KeyError:
        raise LayoutDoesNotExist(name)

def get_grid(name):
    return get_layout(name,True)


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
    
    def __init__(self, *rows, **kwargs):
        self.columns = kwargs.pop('columns',self.columns)
        super(page,self).__init__(*rows, **kwargs)
        #for block in self.blocks():
        #    block.on_layout_done()
    
    def register(self, name):
        name = name.lower()
        _page_layouts['page'][name] = self
        return self
    
    
class grid(elem):
    '''A grid element is the container of rows.'''
    default_class = 'grid-container'
    
    @classmethod
    def childtype(cls):
        return row
    
    def register(self, name):
        name = name.lower()
        _page_layouts['grid'][name] = self
        return self
    
    
class column(elem):
    '''A column is a special container. It is the container which holds djpcms
plugins, unless it has children containers.'''
    default_class = None
    def __init__(self, size = 1, over = 1, *rows, **kwargs):
        self.size = size
        self.over = over
        if self.span > 1:
            raise ValueError('Column span "{0}" is greater than one!'\
                             .format(self.span))
        super(column, self).__init__(*rows, **kwargs)
        
    @property
    def span(self):
        return float(self.size)/self.over
    
    @classmethod
    def childtype(cls):
        return grid
    
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
        

# Simple one row with one column grid
grid_50_50 = grid(
    row()
).register('grid 100')

# Simple layout with single row with two elements of the same size
grid_50_50 = grid(
    row(column(1,2), column(1,2))
).register('grid 50-50')

grid_33_33_33 = grid(
    row(column(1,2), column(1,2))
).register('grid 50-50')

grid_50_50_100 = grid(
    row(column(1,2), column(1,2)),
    row()
).register('grid 33-33-33')


grid(
    row(column(1,2), column(1,2, grid_50_50_100)),
    row()
).register('Grid 50 25-25-50 & 100')


page(container('content')).register('default')
     
