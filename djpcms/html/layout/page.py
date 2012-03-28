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
    return list(_grid_layouts)

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
        
        
class page(elem):
    '''layout for a page. A page contains a list of :class:`container`.'''
    columns = 12
    role = 'page'
    
    def __init__(self, *containers, **kwargs):
        self.columns = kwargs.pop('columns', self.columns)
        if not containers:
            containers = (container('content'),)
        self.renderers = {}
        super(page, self).__init__(*containers, **kwargs)
        
    @classmethod
    def childtype(cls):
        return container 
    
    def get_context(self, request, widget, context):
        # Override get_context to fill up the keyword dictionary
        renderers = self.renderers
        for child in self.allchildren:
            key = child.key
            renderer = self.renderers.get(key)
            if not renderer:
                renderer = self.default_renderer
            context[key] = renderer
        return context
    
    def default_renderer(self, request, block, widget):
        return ''
        
    
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
    

class grid_holder(elem):
    '''A grid holder contains only one :class:`Grid`'''
    def __init__(self, *grid, **kwargs):
        if len(grid) > 1:
            raise RunTimeError('Only one grid can be passed to a grid holder')
        super(grid_holder, self).__init__(*grid, **kwargs)
    
    @classmethod
    def childtype(cls):
        return Grid
    
    def default_inner_grid(self):
        return None
    
    def get_context(self, request, widget, context):
        # Override get_context so that we retrieve the context of
        # underlying blocks if they exists
        page = request.page
        blocks = None
        if not self.allchildren:
            # No children, this could be because this is a block column or
            # a container with key
            if page and self.key == 'content':
                # This is the content
                inner_grid = page.inner_grid
                blocks = page.get_blocks()
            else:
                inner_grid = self.default_inner_grid()
        else:
            inner_grid = self.allchildren[0]
            
        if inner_grid:
            ctx = {}
            # loop over blocks
            for n, block in enumerate(inner_grid.blocks()):
                ctx[block] = n
            return ctx
        else:
            # no inner_grid return the context
            return context
    
    
class container(grid_holder):
    '''A container of a grid system'''
    def __init__(self, key, *grid, **kwargs):
        kwargs['key'] = key
        super(container, self).__init__(*grid, **kwargs)
    
    def default_inner_grid(self):
        return grid('grid 100')
    
    
class column(grid_holder):
    '''A column is a special container. It is the container which holds djpcms
plugins, unless it has children containers.'''
    default_class = None
    def __init__(self, size = 1, over = 1, *grid, **kwargs):
        self.size = size
        self.over = over
        if self.span > 1:
            raise ValueError('Column span "{0}" is greater than one!'\
                             .format(self.span))
        super(column, self).__init__(*grid, **kwargs)
        
    @property
    def span(self):
        return float(self.size)/self.over
    
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
    
    def render_from_widget(self, request, widget, context):
        elem = context.get(self)
        if elem:
            pass
        else:
            return super(column,self).render_from_widget(request, widget,
                                                         context)
    
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
