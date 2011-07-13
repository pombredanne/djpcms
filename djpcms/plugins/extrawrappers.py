from djpcms.plugins import DJPwrapper
from djpcms.html import box


class simplediv(DJPwrapper):
    name = 'flat-element'
    description = 'flat element'
    def wrap(self, djp, cblock, html):
        return '' if not html else '<div class="{0}">\n'.format(self.name)\
                        + html + '\n</div>'


class PannelWrapper(simplediv):
    name = 'flat-panel'
    description = 'panel'
        

class FlatBox(simplediv):
    name = 'flat-box'
    
    def wrap(self, djp, cblock, html):
        if html:
            title = cblock.title
            bd = '<div class="bd">\n' + html + '\n</div>'
            if title:
                bd = '<div class="hd">\n<h2>' + title + '</h2>\n</div>\n' + bd
            return super(FlatBox,self).wrap(djp,cblock,bd)
        else:
            return ''
        
        
class ListWithTitle(simplediv):
    name = 'title-list'
    
    def wrap(self, djp, cblock, html):
        if html and cblock.title:
            html = '<div class="hd ui-widget-header"><h2>{0}</h2></div>{1}'\
                            .format(cblock.title,html)
        return super(ListWithTitle,self).wrap(djp,cblock,html)
    
    
class BoxWrapper(DJPwrapper):
    name = 'box'
    collapsable = False
    collapsed = False
    header_classes = 'ui-widget-header'
    body_classes = 'ui-widget-content'
    footer_classes = 'ui-widget-content'
    
    def wrap(self, djp, cblock, html):
        if html:
            cn,deleteurl = self._wrap(djp, cblock, html)
            return box(id = self.id(cblock),
                       hd = self.title(cblock),
                       bd = html,
                       header_classes = self.header_classes,
                       body_classes = self.body_classes,
                       footer_classes = self.footer_classes,
                       ft = self.footer(djp,cblock,html),
                       collapsable = self.collapsable,
                       collapsed = self.collapsed,
                       delurl = deleteurl,
                       cn = cn)
        else:
            return ''
        
    def title(self, cblock):
        return cblock.title
    
    def id(self, cblock):
        return None
    
    def _wrap(self, djp, cblock, html):
        return None,None
    
    def footer(self, djp, cblock, html):
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

        
