'''Page layout and grids'''
from collections import deque, namedtuple

from .base import WidgetMaker, Widget
from . import classes

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
namespace_columns = namedtuple('namespace_columns','namespace columns')

def get_grid_system(request=None):
    if request: 
        page = request.underlying().page
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

def columns_deque(request, namespace, all_columns, grid):
    '''Return a `deque` containing all columns for a given namespace'''
    num_columns = grid.numcolumns
    new_columns = deque()
    columns = all_columns.get(namespace,{})
    for column in range(num_columns):
        blocks = columns.get(column)
        if blocks is None:
            blocks = {}
        new_blocks = []
        new_columns.append((column,new_blocks))
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
        if build and request.view.Page:
            model = request.view.Page.model
            pageobj = request.page
            if namespace=='content':
                if not pageobj:
                    continue
            else:
                pageobj = None
            block = model.make_block(page=pageobj, column=column, position=np,
                                     namespace=namespace)
            block.save()
            new_blocks.append(block)
    return namespace_columns(namespace, new_columns)

def all_columns(request):
    mapper = request.view.Page
    if not mapper:
        return {}
    model = mapper.model
    pageobj = request.page
    namespaces = {}
    for b in model.blocks(pageobj):
        namespace = get_or_update_dict(namespaces, b.namespace)
        column = get_or_update_dict(namespace, b.column)
        column[b.position] = b
    return namespaces

def edit_blocks(request, blocks):
    '''Renders blocks in editing mode.'''
    for block in blocks:
        edit_block = request.for_model(instance=block, name='change')
        if edit_block:
            yield edit_block.render()
                
def default_renderer(request, namespace, column, blocks):
    '''The default renderer check if plugins are specified'''
    if blocks:
        col_id = 'cms-column-{0}-{1}'.format(namespace, column)
        column = Widget('div', id=col_id, cn='cms-column')
        if request.page_editing:
            column.addClass('sortable-block')
            blocks = edit_blocks(request, blocks)
        else:
            blocks = (block.widget(request) for block in blocks)
        column.add(blocks)
        return column
    elif request:
        return request.render()
    

class PageElemWidget(Widget):
    '''Add the :attr:`numcolumns` attribute to a :class:`Widget`.'''
    @property
    def numcolumns(self):
        return self.maker.numcolumns
    
    
class elem(WidgetMaker):
    '''Base class for all page layout templates. These templates contain all
the information for rendering and styling a web page using a very flexible
grid system.'''
    tag = 'div'
    role = None
    _widget = PageElemWidget
    
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
        cr = widget.internal.get('context_request', context_request)
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
        '''Retrieve the gri system for this request'''
        return get_grid_system(request)
    
    @property
    def numcolumns(self):
        return len(tuple(self.columns()))
    
    def is_column(self):
        '''``True`` if this :class:`elem` is a :class:`column` element'''
        return False
    
    def columns(self):
        '''Generator of columns.'''
        # loop over children
        for child in self.allchildren():
            for column in child.columns():
                yield column
    
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
        self.addClass(classes.wrapper)
        
    @classmethod
    def childtype(cls):
        return container
    
    def get_context(self, request, widget, context):
        context = super(page, self).get_context(request, widget, context)
        if request:
            request = self.context_request(request, widget)
            context['all_columns'] = all_columns(request)
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
        
    def get_context(self, request, widget, context):
        context = super(Grid, self).get_context(request, widget, context)
        columns = context.get('columns')
        # If columns are not available, it means we are using a Grid on its own
        if columns is None:
            cols = deque(((n,[d]) for n,d in enumerate(widget._data_stream)))
            context['columns'] = namespace_columns(None, cols)
            widget._data_stream = []
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
            raise RuntimeError('Only one grid can be passed to a grid holder')
        self.grid_fixed = kwargs.pop('grid_fixed', self.grid_fixed)
        self.renderer = kwargs.pop('renderer', default_renderer)
        super(grid_holder, self).__init__(*grid, **kwargs)
    
    @classmethod
    def childtype(cls):
        return Grid
    
    def default_inner_grid(self, request):
        return None
    
    def get_context(self, request, widget, context):
        # Override get_context so that we retrieve the context of
        # underlying columns if they exists
        context = super(grid_holder, self).get_context(request, widget, context)
        if self.grid_fixed is not None:
            gs = context['grid_system']
            context['grid_system'] = grid_system(self.grid_fixed, gs.columns)
        children = list(widget.allchildren())
        inner_grid = children[0] if children else None
        widget_data = None
        if request:
            request = self.context_request(request, widget)
            pageobj = request.page
        else:
            pageobj = None
        if self.key:
            # if key is context the widget_data is already available
            if self.key in context:
                widget_data = context[self.key]
            # if this is the content, get the inner_grid from the pageobj
            elif self.key == 'content' and pageobj and\
                    pageobj.inner_grid is not None:
                inner_grid = pageobj.inner_grid
        if inner_grid is None:
            inner_grid = self.default_inner_grid(request)
        # this must be a column
        if inner_grid is None:
            data = context.pop('widget_data',None)
            renderer = context.get('renderer')
            if data is None:
                named_columns = context.get('columns')
                col, blocks = named_columns.columns.popleft()
                if renderer:
                    data = renderer(request, named_columns.namespace, col, blocks)
                else:
                    data = blocks
            widget.add(data)
        else:
            all_columns = context.pop('all_columns',{})
            if widget_data is not None:
                context['widget_data'] = widget_data
            else:
                context['columns'] = columns_deque(request, self.key,
                                                   all_columns, inner_grid)
                context['renderer'] = self.renderer
            key = inner_grid.key or 0
            widget.children.clear()
            if isinstance(inner_grid, WidgetMaker):
                inner_grid = self.child_widget(inner_grid, widget)
            widget.children[key] = inner_grid
            return context
            
    
class container(grid_holder):
    '''A container of a grid system. It contains a :class:`grid` element
only. It is associated with a :attr:`WidgetMaker.key` attribute.'''
    def __init__(self, key, *grid, **kwargs):
        key = str(key)
        kwargs['key'] = key
        kwargs['role'] = key
        kwargs['id'] = 'page-'+key
        super(container, self).__init__(*grid, **kwargs)
    
    def default_inner_grid(self, request):
        return grid('grid 100')
    
    
class column(grid_holder):
    '''A column is a special container. It is the container which holds djpcms
plugins, unless it has children containers.'''
    cn = None
    grid_fixed = False
    def __init__(self, size=1, over=1, *grid, **kwargs):
        self.size = size
        self.over = over
        if self.span > 1:
            raise ValueError('Column span "{0}" is greater than one!'\
                             .format(self.span))
        super(column, self).__init__(*grid, **kwargs)
        
    @property
    def span(self):
        return float(self.size)/self.over
    
    def is_column(self):
        return not bool(self.children)
    
    def columns(self):
        '''Override the columns generator since column si special. If there are
no children, it return self as the only child.'''
        if self.is_column():
            yield self
        else:
            for child in super(column, self).columns():
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

Grid(
    row(column(1,4), column(1,2), column(1,4))
).register('grid 25-50-25')
