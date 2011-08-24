from .base import Widget, WidgetMaker


__all__ = ['BoxWidget','box']


class BoxWidget(WidgetMaker):
    tag = 'div'
    default_class = 'djpcms-html-box'
    default_style = 'ui-widget ui-widget-content'
    
    def stream(self, djp, widget, context):
        ediv = '</div>'  
        if widget.hd:
            yield "<div class='hd {0}'>".format(widget.header_classes)
            if widget.title:
                yield "<h2>{0}</h2>".format(widget.title)
            if widget.menulist:
                yield "<div class='edit-menu'>"
                for menu in widget.menulist:
                    yield str(menu)
                yield ediv
            yield ediv
        yield "<div class='bd {0}'>{1}</div>".format(widget.body_classes,widget.bd)
        if widget.ft:
            yield "<div class='ft {0}'>{1}</div>".format(widget.footer_classes,widget.ft)
    

class Box(Widget):
    maker = BoxWidget()
    header_classes = 'ui-widget-header'
    body_classes = 'ui-widget-content'
    footer_classes = 'ui-widget-content'
    
    def __init__(self, hd = None, bd = None, ft = None, header_classes = None,
                 body_classes = None, footer_classes = None, **kwargs):
        self.menulist = []
        self.header_classes = header_classes or self.header_classes
        self.body_classes = body_classes or self.body_classes
        self.footer_classes = header_classes or self.footer_classes
        self.title = None if not hd else hd
        self.hd = 'hd'
        self.bd = None if not bd else bd
        self.ft = None if not ft else ft
        super(Box,self).__init__(**kwargs)
    
    
def box(hd = None, bd = None, ft = None, minimize = False,
        collapsable = False, collapsed = False,
        delurl = None, **kwargs):
    b = Box(hd = hd, bd = bd, ft = ft, **kwargs)
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
