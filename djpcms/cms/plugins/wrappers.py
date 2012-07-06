from djpcms.cms.plugins import DJPwrapper
from djpcms.html import box, Widget, classes


class FlatBox(DJPwrapper):
    name = 'flat'
    description = 'Panel with title'
    
    def render(self, request, block, content):
        return box(hd=block.title, bd=content).addClass(self.name)
        
        
#class ListWithTitle(FlatPanel):
#    name = 'title-list'
#    
#    def render(self, request, cblock, content):
#        if content and cblock.title:
#            html = '<div class="hd ui-widget-header"><h2>{0}</h2></div>{1}'\
#                            .format(cblock.title,html)
#        return super(ListWithTitle,self).render(request,cblock,content)
    
    
class BoxWrapper(DJPwrapper):
    name = 'box'
    collapsable = False
    collapsed = False
    detachable = False
    
    def render(self, request, block, content):
        return box(hd=self.title(block),
                   bd=content,
                   ft=self.footer(request,block,content),
                   id=self.id(block),
                   edit_menu=self.edit_menu(request, block),
                   collapsable=self.collapsable,
                   collapsed=self.collapsed,
                   detachable=self.detachable)
        
    def title(self, block):
        return block.title
    
    def id(self, block):
        return None
    
    def edit_menu(self, request, block):
        pass
    
    def footer(self, request, block, content):
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
