# Widget head
from djpcms.media.style import *
from djpcms.html import classes

cssv.widget.padding = spacing(px(6))
cssv.widget.border.color = cssv.color.grayLight
cssv.widget.border.width = px(1)

cssv.widget.head.background = cssv.color.grayLighter
cssv.widget.head.color = cssv.color.grayDarker
cssv.widget.head.border.color = cssv.color.grayLight
cssv.widget.head.font_size = cssv.heading.h3.font_size
cssv.widget.head.line_height = cssv.heading.h3.line_height
cssv.widget.head.font_weight = cssv.head.font_weight
cssv.widget.head.text_transform = None
cssv.widget.head.padding = cssv.widget.padding

cssv.widget.body.padding = cssv.widget.padding
cssv.widget.body.color = cssv.color.grayDarker
cssv.widget.body.background = cssv.color.white

cssv.panel.color = None
cssv.panel.background = None
cssv.panel.border.color = cssv.widget.border.color
cssv.panel.border.width = cssv.widget.border.width


css('.'+classes.widget,
    cssb('.hd',
         padding_top=0,
         padding_bottom=0),
    cssb('.bd',
         padding=cssv.widget.body.padding,
         overflow='hidden',
         border='none',
         display='block'),
    cssb('.ft',
         padding=cssv.widget.foot.padding,
         overflow='hidden',
         border='none')
)

cssb('.'+classes.widget_body,
     bcd(**cssv.widget.body.params()),
     padding=cssv.widget.body.padding),
         
css('.'+classes.widget_head,
    bcd(**cssv.widget.head.params()),
    border(**cssv.widget.head.border.params()),
    css('h1,h2,h3,h4,h5',
        font_size=cssv.widget.head.font_size,
        font_weight=cssv.widget.head.font_weight,
        text_transform=cssv.widget.head.text_transform,
        line_height=cssv.widget.head.line_height,
        float='left',
        padding=0,
        margin=0,
        background='transparent'
    ),
    css('.'+classes.edit_menu,
        line_height=cssv.widget.head.line_height),
    padding=cssv.widget.head.padding,
    overflow='hidden')

################################################# PANEL
css('.'+classes.widget_body,
    cssa('.panel',
         bcd(**cssv.panel.params()),
         border(**cssv.panel.border.params())))

################################################################ RADIUS
css('.'+classes.corner_all,
    radius(cssv.body.radius))

css('.'+classes.corner_top,
    radius(spacing(cssv.body.radius, cssv.body.radius, 0, 0)))

css('.'+classes.corner_bottom,
    radius(spacing(0, 0, cssv.body.radius, cssv.body.radius)))