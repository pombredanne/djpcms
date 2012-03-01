from .base import WidgetMaker

_page_layouts = {}

class LayoutDoesNotExist(Exception):
    pass


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
        widgets = tuple((w for w in widgets if isinstance(w, child)))
        return super(PageLayoutElement,self).add(*widgets)
    
    def on_layout_done(self):
        pass
    
    @classmethod
    def childtype(cls):
        raise NotImplementedError()

    def render_from_widget(self, request, widget, context):
        grid = request.cssgrid()
        self.add_grid_data(grid, widget)
        return super(PageLayoutElement,self).render_from_widget(
                                            request, widget, context)
    
    def add_grid_data(self, grid, widget):
        pass
        

class PageBlockElement(PageLayoutElement):
    
    @property
    def columns(self):
        return self.parent.columns


class page(PageLayoutElement):
    '''layout for a page'''
    child_maker = PageLayoutElement
    
    def __init__(self, *rows, **kwargs):
        self.columns = kwargs.pop('columns',self.columns)
        super(page,self).__init__(*rows, **kwargs)
        for block in self.blocks():
            block.on_layout_done()
    
    def add_grid_data(self, grid, widget):
        main = not isinstance(self.parent, page)
        widget.addClass(grid.page_class(main))
    
    @classmethod
    def childtype(cls):
        return (page,row)
    
    def register(self, name):
        name = name.lower()
        _page_layouts[name] = self
        return self


class column(PageBlockElement):
    
    def __init__(self, size = 1, over = 1, *rows, **kwargs):
        self.size = size
        self.over = over
        if self.span > 1:
            raise ValueError('Column span "{0}" is greater than one!'\
                             .format(self.span))
        super(column, self).__init__(*rows, **kwargs)

    def add_grid_data(self, grid, widget):
        widget.addClass(grid.column_class(self.size,self.over))
        
    @property
    def span(self):
        return float(self.size)/self.over
    
    @classmethod
    def childtype(cls):
        return row
        
        
class row(PageBlockElement):
    
    def __init__(self, *columns, **kwargs):
        if not columns:
            columns = (column(),)
        super(row, self).__init__(*columns, **kwargs)

    def add_grid_data(self, grid, widget):
        if isinstance(self.parent,page): # main row
            widget.addClass(grid.rowclass)
        else:   # secondary row
            widget.addClass(grid.secondary_rowclass)
            
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
