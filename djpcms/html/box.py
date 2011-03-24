from .base import HtmlWidget


class BoxWidget(HtmlWidget):
    tag = 'div'
    template = ('box.html','djpcms/components/box.html')
    header_classes = 'ui-widget-header'
    
    def __init__(self, hd = None, bd = None, ft = None, header_classes = None, **kwargs):
        self.menulist = []
        self.header_classes = header_classes or self.header_classes
        self._ctx = {'title': None if not hd else hd,
                     'hd': True,
                     'bd': None if not bd else bd,
                     'ft': None if not ft else ft,
                     'header_classes':self.header_classes,
                     'menulist': self.menulist}
        super(BoxWidget,self).__init__(**kwargs)
        
    def get_context(self, context):
        context.update(self._ctx)
        
    
    
def box(hd = None, bd = None, ft = None, minimize = False,
        collapsable = False, collapsed = False, delurl = None, **kwargs):
    b = BoxWidget(hd = hd, bd = bd, ft = ft, **kwargs).addClass('djpcms-html-box ui-widget')
    menulist = b.menulist
    cn = 'ui-icon-circle-triangle-n'
    if collapsed:
        cn = 'ui-icon-circle-triangle-s'
        b.addClass('collapsed')
        collapsable = True
    if collapsable:
        b.addClass('collapsable')
        menulist.append('<a class="collapse" href="#"><span class="ui-icon {0}"></span></a>'.format(cn))
    if delurl:
        menulist.append('<a class="ajax" href="{0}"><span class="ui-icon ui-icon-closethick"></span></a>'.format(delurl))
    return b.render()