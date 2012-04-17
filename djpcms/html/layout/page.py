'''Page layout and grids
'''
from collections import deque

from djpcms.html import WidgetMaker

__all__ = ['LayoutDoesNotExist',
           'grid_systems',
           'equally_spaced_grid',
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
        if isinstance(maker, row):
            if isinstance(maker.parent.parent, container) and self.fixed:
                widget.addClass('row-{0}'.format(self.columns))
            else:
                widget.addClass('row-fluid-{0}'.format(self.columns))
        elif isinstance(maker, column):
            span = maker.size * self.columns // maker.over
            widget.addClass('span{0}'.format(span))
        elif isinstance(maker, Grid):
            if isinstance(maker.parent, container) and self.fixed:
                widget.addClass('grid-container-{0}'.format(self.columns))
            else:
                widget.addClass('grid-container-fluid-{0}'.format(self.columns))
    

class elem(WidgetMaker):
    '''A page layout contains all the information for rendering and styling a
web page using a very flexible grid system.'''
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
        for child in self.allchildren():
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

    def stream_from_widget(self, request, widget, context):
        #grid = request.cssgrid()
        grid = CssGrid()
        grid.add_css_data(widget)
        return super(elem,self).stream_from_widget(
                               request, widget, context)
    
    
class page(elem):
    '''HTML layout for a page. It is the first (and only) div element within
the body tag. A page contains a list of :class:`container`.'''
    columns = 12
    role = 'page'
    
    def __init__(self, *containers, **kwargs):
        self.columns = kwargs.pop('columns', self.columns)
        if not containers:
            containers = (container('content'),)
        super(page, self).__init__(*containers, **kwargs)
        
    @classmethod
    def childtype(cls):
        return container
    
    def get_context(self, request, widget, context):
        # Override get_context to fill up the keyword dictionary
        page = request.page if request else None
        context = context if context is not None else {}
        block_dictionary = page.block_dictionary() if page is not None else {}
        for child in self.allchildren():
            key = child.key
            if key in context:
                renderer = context[key]
            else:
                renderer = child.renderer
                if not renderer:
                    renderer = self.default_renderer
            blocks = block_dictionary.get(key)
            context[key] = {'renderer': renderer,
                            'blocks': blocks if blocks is not None else {}}
        return context
    
    def default_renderer(self, request, block_number, blocks):
        '''The default renderer check if plugins are specified'''
        if blocks:
            for position in sorted(blocks):
                block = blocks[position]
        elif request:
            return request.render()
                
        
class Grid(elem):
    '''A grid element is the container of rows.'''
    tag = 'div'
    
    def __init__(self, *rows, **kwargs):
        cleaned_rows = []
        for row in rows:
            if isinstance(row, Grid):
                cleaned_rows.extend(row.allchildren())
            else:
                cleaned_rows.append(row)
        super(Grid, self).__init__(*cleaned_rows, **kwargs)
        
    @classmethod
    def childtype(cls):
        return row
    
    def get_context(self, request, widget, context):
        renderer = None
        if context:
            renderer = context.get('renderer')
            all_blocks = context.get('blocks')
            if all_blocks is None:
                all_blocks = {}
        queue = deque()
        if not renderer:
            queue.extend(widget._data_stream)
            widget._data_stream = []
        else:
            for n, wm in enumerate(self.blocks()):
                blocks = all_blocks.get(n)
                queue.append(renderer(request, n, blocks))
        return {'blocks': queue}
            
    def register(self, name):
        name = name.lower()
        _grid_layouts[name] = self
        return self
    

class grid_holder(elem):
    '''A grid holder can contain only one :class:`Grid`'''
    def __init__(self, *grid, **kwargs):
        if len(grid) > 1:
            raise RunTimeError('Only one grid can be passed to a grid holder')
        super(grid_holder, self).__init__(*grid, **kwargs)
    
    @classmethod
    def childtype(cls):
        return Grid
    
    def default_inner_grid(self, request):
        return None
    
    def get_context(self, request, widget, context):
        # Override get_context so that we retrieve the context of
        # underlying blocks if they exists
        children = list(self.allchildren())
        inner_grid = children[0] if children else None
        if self.key:
            page = request.page if request else None
            if self.key == 'content' and page:
                inner_grid = page.inner_grid or inner_grid
            if not inner_grid and self.key == 'content':
                # No inner grid for content. Set the default inner grid
                inner_grid = self.default_inner_grid(request)
        if inner_grid:
            key = inner_grid.key or 0
            widget.children.clear()
            widget.children[key] = self.child_widget(inner_grid, widget)
            return context
        elif context and 'blocks' in context:
            widget.add(context['blocks'].popleft())
            
    
class container(grid_holder):
    '''A container of a grid system'''
    def __init__(self, key, *grid, **kwargs):
        key = str(key)
        kwargs['key'] = key
        kwargs['role'] = key
        kwargs['id'] = 'page-'+key
        self.renderer = kwargs.pop('renderer',None)
        super(container, self).__init__(*grid, **kwargs)
    
    def default_inner_grid(self, request):
        return grid('grid 100')
    
    
class column(grid_holder):
    '''A column is a special container. It is the container which holds djpcms
plugins, unless it has children containers.'''
    cn = None
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
        return not bool(self.children)
    
    def blocks(self):
        '''Override the blocks generator since column si special. If there are
no children, it return self as the only child.'''
        if self.is_block():
            yield self
        else:
            for child in super(column, self).blocks():
                yield child
                
    
class row(elem):
    '''A row element contains columns. It is rendered as a div element
with row or row-fluid class.'''
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
        

def equally_spaced_grid(ncols):
    pc = 100//ncols
    pcs = str(pc)
    name = 'grid ' + '-'.join([pcs]*ncols)
    grid = _grid_layouts.get(name)
    if not grid:
        cols = [column(1,ncols)]*ncols
        grid = Grid(row(*cols)).register(name)
    return grid
    
# Simple grids registration
equally_spaced_grid(1)
equally_spaced_grid(2)
equally_spaced_grid(3)
equally_spaced_grid(4)
equally_spaced_grid(6)

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
