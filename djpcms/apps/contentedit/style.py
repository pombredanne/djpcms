from djpcms.media.style import *
from .classes import edit as content_edit

# content edit page panel
cssv.cedit.background = cssv.color.grayDarker
cssv.cedit.border.color = cssv.cedit.background
cssv.cedit.color = cssv.color.white
cssv.cedit.font_size = pc(90)
cssv.cedit.link.hover.text_decoration = 'none'
cssv.cedit.link.default.color = cssv.color.grayLighter
cssv.cedit.link.hover.color = lazy(color.darken,
                                  cssv.edit.link.default.color, 15)

css('.'+content_edit,
    gradient(cssv.cedit.background),
    css('.%s.%s' % (classes.widget, content_edit),
        gradient(cssv.cedit.background)))

css('.%s.%s' % (classes.widget, content_edit),
    cssb('.'+classes.widget_head,
         bcd(**cssv.cedit.params())),
    cssb('.'+classes.widget_body,
         bcd(**cssv.cedit.params())),
    cssb('.'+classes.widget_foot,
         border='none',
         padding=spacing(px(3), 0, 0),
         background='transparent'),
    css('.cms-block',
        margin_bottom=0),
    border='none',
    background='transparent')