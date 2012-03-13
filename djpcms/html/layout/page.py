'''Page layout and grids
'''
from djpcms.html import WidgetMaker

__all__ = ['LayoutDoesNotExist', 'get_layout', 'page_layouts',
           'page', 'container', 'inner_container', 'row', 'column']


_page_layouts = {'page': {},
                 'inner': {}}


class LayoutDoesNotExist(Exception):
    pass


def page_layouts(inner = False):
    return sorted(_page_layouts['page'])

def get_layout(name, inner = False):
    pages = _page_layouts['inner' if inner else 'page']
    try:
        return pages[name.lower()]
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
    

class PageLayoutElement(WidgetMaker):
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
        super(PageLayoutElement,self).__init__(**kwargs)
        self.add(*children)
        
    def numblocks(self):
        return sum((c.numblocks() for c in self.allchildren))
    
    def blocks(self):
        for child in self.allchildren:
            cb = 0
            for c in child.blocks():
                cb += 1
                yield c
            if not cb:
                yield child
                
    #def add(self, *widgets):
    #    child = self.childtype()
    #    for w in widgets:
    #        if not isinstance(w, child):
    #            raise ValueError('"{0}" cannot be a child of "{1}".'\
    #                             .format(w,self))
    #    return super(PageLayoutElement,self).add(*widgets)
    
    def on_layout_done(self):
        pass
    
    @classmethod
    def childtype(cls):
        raise NotImplementedError()

    def render_from_widget(self, request, widget, context):
        #grid = request.cssgrid()
        grid = CssGrid()
        grid.add_css_data(widget)
        return super(PageLayoutElement,self).render_from_widget(
                                            request, widget, context)
        

class container(WidgetMaker):
    '''This act as a container for its children. It does not render
to anything'''
    def __init__(self, key):
        super(container,self).__init__(key = key)
    
    def render_from_widget(self, request, widget, context):
        return context['inner']
    
    
class PageBlockElement(PageLayoutElement):
    
    @property
    def columns(self):
        return self.parent.columns


class page(PageLayoutElement):
    '''layout for a page'''
    columns = 12
    role = 'page'
    
    def __init__(self, *rows, **kwargs):
        self.columns = kwargs.pop('columns',self.columns)
        super(page,self).__init__(*rows, **kwargs)
        #for block in self.blocks():
        #    block.on_layout_done()
    
    @classmethod
    def childtype(cls):
        return (container,)
    
    def register(self, name):
        name = name.lower()
        _page_layouts['page'][name] = self
        return self
    
    
class grid(PageBlockElement):
    '''A container is a block inside a page which support grid layout.'''
    role = 'content'
    default_class = 'grid-container'
    
    def register(self, name):
        name = name.lower()
        _page_layouts['inner'][name] = self
        return self
    
    
class inner(container):
    tag = None
    def add(self, *widgets):
        pass
    
    def render_from_widget(self, request, widget, context):
        return context['inner']
    
    
class inner_container(container):
    pass
    
    
class column(PageBlockElement):
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
        
        
class row(PageBlockElement):
    
    def __init__(self, *columns, **kwargs):
        if not columns:
            columns = (column(),)
        super(row, self).__init__(*columns, **kwargs)
        
    @classmethod
    def childtype(cls):
        return column
    

# Simple layout with single row with two elements of the same size
grid(
    row(column(1,2), column(1,2))
).register('Grid 50-50')

grid(
    row(column(1,2), column(1,2)),
    row()
).register('Grid 50-50 & 100')


grid(
    row(column(1,2), column(1,2, row(column(1,2),column(1,2)), row())),
    row()
).register('Grid 50 25-25-50 & 100')


page(container('content')).register('default')
     
page(container('header'),
     container('content'),
     container('footer')).register('header-content-footer')

#page_layout(
#    page_row(grid(1,2), grid(1,2).add(fixed_tabs(2))),
#    page_row()
#).register('960 Grid 50-50')
