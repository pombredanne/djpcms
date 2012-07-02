# Widget head
from djpcms.media.style import *
from djpcms.html import classes

cssv.clickable.default.background = ('v', color('#e6e6e6'), color.darken('#e6e6e6',10))
cssv.clickable.default.color = color('#555')
cssv.clickable.default.text_decoration = 'none'
cssv.clickable.default.border.color = color('d3d3d3')
cssv.clickable.default.border.width = None
cssv.clickable.default.border.style = None
#
cssv.clickable.hover.background = ('v', color('#dadada'), color.darken('#dadada',10))
cssv.clickable.hover.color = color('#555')
cssv.clickable.hover.text_decoration = 'none'
cssv.clickable.hover.border.color = color('999999')
cssv.clickable.hover.border.width = None
cssv.clickable.hover.border.style = None
#
cssv.clickable.active.background = color('#fff')
cssv.clickable.active.color = color('#212121')
cssv.clickable.active.text_decoration = 'none'
cssv.clickable.active.border.color = color('aaaaaa')
cssv.clickable.active.border.width = None
cssv.clickable.active.border.style = None

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


css('body',
    css_include(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'media','ui.css')))

############################################################### CLICKABLE
css('.'+classes.clickable,
    clickable(default=bcd(**cssv.clickable.default.params()),
              hover=bcd(**cssv.clickable.hover.params()),
              active=bcd(**cssv.clickable.active.params())),
    css('a', text_decoration='none', color='inherit',
        font_weight='inherit', cursor='inherit'))
    
    
############################################################### WIDGET
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

radius_top = spacing(cssv.body.radius, cssv.body.radius, 0, 0)
radius_bottom = spacing(0, 0, cssv.body.radius, cssv.body.radius)

css('.'+classes.corner_top, radius(radius_top))
css('.'+classes.corner_bottom, radius(radius_bottom))