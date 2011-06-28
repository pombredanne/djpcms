from djpcms.template import loader

from .base import Widget, WidgetMaker


class BoxWidget(WidgetMaker):
    tag = 'div'
    template = loader.template_class('''\
{% if widget.hd %}
 <div class="hd {{ widget.header_classes }}">
  <h2>{% if widget.title %}{{ widget.title }}{% endif %}</h2>{% if widget.menulist %}
  <div class="edit-menu">{% for menu in widget.menulist %}
   {{ menu }}{% endfor %}
  </div>{% endif %}
 </div>{% endif %}
 <div class="bd {{ widget.body_classes }}">
 {{ widget.bd }}
 </div>{% if widget.ft %}
 <div class="ft {{ widget.footer_classes }}">
 {{ widget.ft }}
 </div>{% endif %}''')
    

class Box(Widget):
    maker = BoxWidget()
    header_classes = 'ui-widget-header'
    body_classes = 'ui-widget-content'
    footer_classes = 'ui-widget-content'
    def __init__(self, hd = None, bd = None, ft = None, header_classes = None,
                 body_classes = None, footer_classes = None, **kwargs):
        self.menulist = []
        self.header_classes = header_classes or self.header_classes
        self.body_classes = body_classes or self.header_classes
        self.footer_classes = header_classes or self.footer_classes
        self.title = None if not hd else hd
        self.hd = 'hd'
        self.bd = None if not bd else bd
        self.ft = None if not ft else ft
        super(Box,self).__init__(**kwargs)
    
    
def box(hd = None, bd = None, ft = None, minimize = False,
        collapsable = False, collapsed = False, delurl = None, **kwargs):
    b = Box(hd = hd, bd = bd, ft = ft, **kwargs).addClass('djpcms-html-box ui-widget')
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