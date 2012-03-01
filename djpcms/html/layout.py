from .base import WidgetMaker

_page_layouts = {}

class PageLayoutElement(WidgetMaker):
    
    def numblocks(self):
        return sum((c.numblocks() for c in self.allchildren))
    
    def add(self, *widgets):
        widgets = tuple((w for w in widgets\
                          if isinstance(widget, PageLayoutElement)))
        super(PageLayoutElement,self).add(*widgets)
        

class PageLayout(PageLayoutElement):
    
    def register(self, name):
        name = name.lower()
        if name in _page_layouts:
            raise KeyError('Layout "{0}" already registered'.format(name))
        _page_layouts[name] = self
        return self
    
    
class PageBlock(PageLayoutElement):
    pass
    
    
class grid_row(*blocks):
    pass
        
    
def page_layout(*rows, **kwargs):
    '''Each row is an instance of grid_row'''
    wl = PageLayout(**kwargs)
    counter = 0
    for row in rows:
        counter += row.count()
        wl.add(row)
    return wl



page_layout(
    page_row(grid(1,2), grid(1,2)),
    page_row(grid())
).register('960 Grid 50-50')


page_layout(
    grid_row(grid360e(2,3), grid360e(1,3)),
    grid_row(grid360e())
).register('960 Grid 66-33 & 100')


page_layout(
    page_row(grid(1,2), grid(1,2).add(fixed_tabs(2))),
    page_row(grid())
).register('960 Grid 50-50')
        