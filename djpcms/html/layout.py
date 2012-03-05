'''Grid layouts for pages.
'''
from .base import WidgetMaker

_page_layouts = {}

class LayoutDoesNotExist(Exception):
    pass


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
    
    
def page_layouts():
    return sorted(_page_layouts)

def get_layout(name):
    try:
        return _page_layouts[name.lower()]
    except KeyError:
        raise LayoutDoesNotExist(name)


class PageLayoutElement(WidgetMaker):
    tag = 'div'
    
    def __init__(self, *children, **kwargs):
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
                
    def add(self, *widgets):
        child = self.childtype()
        for w in widgets:
            if not isinstance(w, child):
                raise ValueError('"{0}" cannot be a child of "{1}".'\
                                 .format(w,self))
        return super(PageLayoutElement,self).add(*widgets)
    
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
        

class PageBlockElement(PageLayoutElement):
    
    @property
    def columns(self):
        return self.parent.columns


class page(PageLayoutElement):
    '''layout for a page'''
    columns = 12
    
    def __init__(self, *rows, **kwargs):
        self.columns = kwargs.pop('columns',self.columns)
        super(page,self).__init__(*rows, **kwargs)
        for block in self.blocks():
            block.on_layout_done()
    
    @classmethod
    def childtype(cls):
        return (page,container,row)
    
    def register(self, name):
        name = name.lower()
        _page_layouts[name] = self
        return self


class inner(PageLayoutElement):
    tag = None
    def add(self, *widgets):
        pass
    
    def render_from_widget(self, request, widget, context):
        return context['inner']
    
    
class container(PageBlockElement):
    default_class = 'grid-container'
    @classmethod
    def childtype(cls):
        return (row,page,inner)
    
    
class column(container):
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
page(
    row(column(1,2), column(1,2))
).register('Grid 50-50')

page(
    row(column(1,2), column(1,2)),
    row()
).register('Grid 50-50 & 100')


page(
    row(column(1,2), column(1,2, row(column(1,2),column(1,2)), row())),
    row()
).register('Grid 50 25-25-50 & 100')


#page_layout(
#    page_row(grid(1,2), grid(1,2).add(fixed_tabs(2))),
#    page_row()
#).register('960 Grid 50-50')
