from djpcms.cms.plugins import DJPwrapper
from djpcms.html import box, Widget, classes


class FlatPanel(DJPwrapper):
    name = 'panel'
    description = 'Panel'
    def wrap(self, request, block, html):
        return Widget('div', html,
                      cn=(self.name, classes.widget_body, classes.corner_all))


class FlatBox(DJPwrapper):
    name = 'flat'
    description = 'Panel with title'
    
    def wrap(self, request, block, html):
        return box(hd=block.title, bd=html).addClass(self.name)
        
        
class ListWithTitle(FlatPanel):
    name = 'title-list'
    
    def wrap(self, request, cblock, html):
        if html and cblock.title:
            html = '<div class="hd ui-widget-header"><h2>{0}</h2></div>{1}'\
                            .format(cblock.title,html)
        return super(ListWithTitle,self).wrap(request,cblock,html)
    
    
class BoxWrapper(DJPwrapper):
    name = 'box'
    collapsable = False
    collapsed = False
    detachable = False
    
    def wrap(self, request, block, html):
        return box(hd=self.title(block),
                   bd=html,
                   ft=self.footer(request,block,html),
                   id=self.id(block),
                   edit_menu=self.edit_menu(request, block),
                   collapsable=self.collapsable,
                   collapsed=self.collapsed,
                   detachable=self.detachable)\
                    .addClass(self.extra_class(request, block, html))
        
    def title(self, block):
        return block.title
    
    def id(self, block):
        return None
    
    def edit_menu(self, request, block):
        pass
    
    def extra_class(self, request, block, html):
        return None
    
    def footer(self, request, block, html):
        return ''
        
        
class CollapseWrapper(BoxWrapper):
    name = 'box-collapse'
    description = 'box collapsable'
    collapsable = True


class CollapsedWrapper(BoxWrapper):
    name = 'box-collapse-closed'
    description = 'box collapsable closed'
    collapsable = True
    collapsed = True


class DetachableBox(BoxWrapper):
    name = 'box-detach'
    description = 'box detachable'
    detachable = True        
