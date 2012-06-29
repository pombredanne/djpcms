from djpcms.media.style import *
from .classes import edit as content_edit

# edit page panel
cssv.cedit.background = cssv.color.grayDarker
cssv.cedit.border.color = cssv.cedit.background 
cssv.cedit.color = cssv.color.white
cssv.cedit.font_size = pc(90)
cssv.cedit.link.hover.text_decoration = 'none'
cssv.cedit.link.default.color = cssv.color.grayLighter
cssv.cedit.link.hover.color = lazy(color.darken,
                                  cssv.edit.link.default.color, 15)


css('.'+classes.widget,
    cssa('.'+content_edit,
         cssb('.'+classes.widget_head,
              bcd(**cssv.cedit.params())),
         cssb('.'+classes.widget_body,
              bcd(**cssv.cedit.params())),
         css('.cms-block',
             margin_bottom=0),
         border(**cssv.cedit.border.params())))