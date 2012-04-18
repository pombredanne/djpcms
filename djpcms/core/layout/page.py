'''Page layout and grids
'''
from collections import deque, namedtuple

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


grid_system = namedtuple('grid_system','fixed columns')

def get_grid_system(request=None):
    if request: 
        page = request.page
        system = page.grid_system if page else None
        system = system or request.settings.LAYOUT_GRID_SYSTEM
    try:
        fixed, columns = system.split('_')
        fixed = fixed == 'fixed'
        columns = int(columns)
    except:
        fixed = True
        columns = 12
    return grid_system(fixed, columns)


class LayoutDoesNotExist(Exception):
    pass


def grids():
    return list(_grid_layouts)

def grid(name):
    try:
        return _grid_layouts[name.lower()]
    except KeyError:
        raise LayoutDoesNotExist(name)


context_request = lambda request: request.underlying()


def get_or_update_dict(d, key, val = None):
    if key not in d:
        d[key] = val if val is not None else {}
    return d[key]

def block_dictionary(all_blocks, grid):
    numblocks = grid.numblocks
    for nb in range(numblocks):
        blocks = content.get(nb)
        if blocks is None:
            blocks = {}
        content[nb] = new_blocks = []
        np = 0
        build = True
        for p in sorted(blocks):
            block = blocks.pop(p)
            if not block.plugin_name and blocks:
                block.delete()
                continue
            if block.position != np:
                block.position = np
                block.save()
            if not block.plugin_name:
                build = False
            new_blocks.append(block)
            np += 1
        if build:
            block = model.make_block(page=pageobj, block=nb, position=np)
            block.save()
            new_blocks.append(block)                
    return blockcontent

def all_blocks(request):
    mapper = request.view.Page
    if not mapper:
        return {}
    model = mapper.model
    pageobj = request.page
    blockcontent = {}
    for b in model.blocks(pageobj):
        namespace = get_or_update_dict(blockcontent, b.namespace)
        blocks = get_or_update_dict(namespace, b.block)
        blocks[b.position] = b
    return blocks
    

class elem(WidgetMaker):
    '''Base class for all page layout templates. These templates contain all
the information for rendering and styling a web page using a very flexible
grid system.'''
    tag = 'div'
    role = None
    
    def __init__(self, *children, **kwargs):
        role = kwargs.pop('role',self.role)
        if role:
            data = kwargs.get('data',{})
            data['role'] = role
            kwargs['data'] = data
        cr = kwargs.pop('context_request', None)
        super(elem, self).__init__(**kwargs)
        if cr:
            self.internal['context_request'] = cr
        self.add(*children)
        
    def context_request(self, request, widget):
        cr = widget.internal.get('context_request',context_request)
        return cr(request)
    
    def get_context(self, request, widget, context):
        context = context.copy() if context is not None else {}
        grid = context.get('grid_system')
        if not grid:
            grid = self.get_grid_system(request, widget, context)
        if grid:
            context['grid_system'] = grid
            self.add_css_data(widget, grid)
        return context
            
    def get_grid_system(self, request, widget, context):
        pass
    
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
        
    def add_css_data(self, widget, grid):
        pass
    
    
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
    
    def get_grid_system(self, request, widget, context):
        return get_grid_system(request)
    
    def get_context(self, request, widget, context):
        context = super(Grid, self).get_context(request, widget, context)
        if request:
            request = self.context_request(request, widget)
            context['all_blocks'] = all_blocks(request)
        return context
                
        
class Grid(elem):
    '''A grid element is the container of :class:`row`.'''
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
    
    def get_grid_system(self, request, widget, context):
        return grid_system(False, 12)
        
    def get_context(self, request, widget, context):
        context = super(Grid, self).get_context(request, widget, context)
        if request:
            request = self.context_request(request, widget)
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
        context['blocks'] = queue
        return context
            
    def register(self, name):
        name = name.lower()
        _grid_layouts[name] = self
        return self
    
    def add_css_data(self, widget, grid):
        parent = widget.parent
        #ADD CLASS ONLY IF PARENT IS A CONTAINER
        if parent is not None and isinstance(parent.maker, container):
            suffix = ('{0}' if grid.fixed else 'fluid-{0}').format(grid.columns)
            widget.addClass('grid-container-'+suffix)
    

class grid_holder(elem):
    '''A grid holder can contain one :class:`Grid` element or nothing. If
it doesn't contain anything this must be a :class:`column` or a
default :class:`Grid` element is created.'''
    grid_fixed = None
    def __init__(self, *grid, **kwargs):
        if len(grid) > 1:
            raise RunTimeError('Only one grid can be passed to a grid holder')
        self.grid_fixed = kwargs.pop('grid_fixed', self.grid_fixed)
        super(grid_holder, self).__init__(*grid, **kwargs)
    
    @classmethod
    def childtype(cls):
        return Grid
    
    def default_inner_grid(self, request):
        return None
    
    def get_context(self, request, widget, context):
        # Override get_context so that we retrieve the context of
        # underlying blocks if they exists
        context = super(grid_holder, self).get_context(request, widget, context)
        if self.grid_fixed is not None:
            gs = context['grid_system']
            context['grid_system'] = grid_system(self.grid_fixed, gs.columns)
        children = list(widget.allchildren())
        inner_grid = children[0] if children else None
        if request:
            request = self.context_request(request, widget)
            pageobj = request.page
        else:
            pageobj = None
        if self.key:
            # if this is the content, get the inner_grid from the pageobj
            if self.key == 'content' and pageobj:
                inner_grid = pageobj.inner_grid or inner_grid
            if not inner_grid and self.key == 'content':
                # No inner grid for content. Set the default inner grid
                inner_grid = self.default_inner_grid(request)
        # No inner grid and blocks in context, this is a column
        if not inner_grid and 'blocks' in context:
            widget.add(context['blocks'].popleft())
        else:
            blocks = context.get('all_blocks',{}).get(self.key)
            inner_grid = inner_grid or self.default_inner_grid(request)
            blocks = block_dictionary(blocks, request, inner_grid)
            key = inner_grid.key or 0
            widget.children.clear()
            widget.children[key] = self.child_widget(inner_grid, widget)
        return context
            
    
class container(grid_holder):
    '''A container of a grid system'''
    def __init__(self, key, *grid, **kwargs):
        key = str(key)
        kwargs['key'] = key
        kwargs['role'] = key
        kwargs['id'] = 'page-'+key
        self.renderer = kwargs.pop('renderer', None)
        super(container, self).__init__(*grid, **kwargs)
    
    def default_inner_grid(self, request):
        return grid('grid 100')
    
    
class column(grid_holder):
    '''A column is a special container. It is the container which holds djpcms
plugins, unless it has children containers.'''
    cn = None
    grid_fixed = False
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
                
    def add_css_data(self, widget, grid):
        span = self.size * grid.columns // self.over
        widget.addClass('span{0}'.format(span))
                
    
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
    
    def add_css_data(self, widget, grid):
        suffix = ('{0}' if grid.fixed else 'fluid-{0}').format(grid.columns)
        widget.addClass('row-'+suffix)
        
    
    
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
