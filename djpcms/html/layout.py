from .base import WidgetMaker

__all__ = ['LayoutDoesNotExist',
           'page_layouts',
           'get_layout',
           'PageLayout',
           'PageLayoutElement',
           'PageBlock',
           'page_layout',
           'page_row',
           'grid']

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
    child_maker = None    
    def numblocks(self):
        return sum((c.numblocks() for c in self.allchildren))
    
    def add(self, *widgets):
        child = self.child_maker or self.__class__
        widgets = tuple((w for w in widgets if isinstance(w, child)))
        return super(PageLayoutElement,self).add(*widgets)
        

class PageLayout(PageLayoutElement):
    child_maker = PageLayoutElement
    
    def register(self, name):
        name = name.lower()
        _page_layouts[name] = self
        return self
    
    
class PageBlockElement(PageLayoutElement):
    pass


class grid(PageBlockElement):
    child_maker = PageBlockElement
    def __init__(self, size = 1, over = 1, **kwargs):
        self.size = size
        self.over = over
        if float(size) / over > 1:
            raise ValueError('Grid has size bigger than one')
        super(grid, self).__init__(**kwargs)
        

class PageBlock(PageLayoutElement):
    child_maker = PageBlockElement


def page_row(*blocks, **kwargs):
    block = PageBlock(**kwargs)
    if not blocks:
        blocks = (PageBlockElement(),)
    block.add(*blocks)
    return block

    
def page_layout(*rows, **kwargs):
    '''Each row is an instance of grid_row'''
    wl = PageLayout(**kwargs)
    return wl.add(*rows)


page_layout(
    page_row(grid(1,2), grid(1,2)),
    page_row(grid())
).register('Grid 50-50')


page_layout(
    page_row(grid(2,3), grid(1,3)),
    page_row()
).register('Grid 66-33 & 100')


#page_layout(
#    page_row(grid(1,2), grid(1,2).add(fixed_tabs(2))),
#    page_row()
#).register('960 Grid 50-50')
