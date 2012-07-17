# Widget head
from djpcms.media.style import *
from djpcms.html import classes

cssv.clickable.radius = cssv.body.radius
cssv.clickable.default.background = ('v', color('#e6e6e6'), color.darken('#e6e6e6',10))
cssv.clickable.default.color = color('#555')
cssv.clickable.default.text_decoration = 'none'
cssv.clickable.default.border.color = color('d3d3d3')
cssv.clickable.default.border.width = px(1)
cssv.clickable.default.border.style = None
#
cssv.clickable.hover.background = ('v', color('#dadada'), color.darken('#dadada',10))
cssv.clickable.hover.color = color('#555')
cssv.clickable.hover.text_decoration = 'none'
cssv.clickable.hover.border.color = color('999999')
cssv.clickable.hover.border.width = cssv.clickable.default.border.width
cssv.clickable.hover.border.style = None
#
cssv.clickable.active.background = color('#fff')
cssv.clickable.active.color = color('#212121')
cssv.clickable.active.text_decoration = 'none'
cssv.clickable.active.border.color = color('aaaaaa')
cssv.clickable.active.border.width = cssv.clickable.default.border.width
cssv.clickable.active.border.style = None

cssv.widget.padding = spacing(px(6))
cssv.widget.border.color = cssv.color.grayLight
cssv.widget.border.width = px(1)
cssv.widget.border.style = None

cssv.widget.head.background = cssv.color.grayLighter
cssv.widget.head.color = cssv.color.grayDarker 
cssv.widget.head.font_size = cssv.heading.h3.font_size
cssv.widget.head.line_height = cssv.heading.h3.font_size
cssv.widget.head.font_weight = cssv.head.font_weight
cssv.widget.head.text_transform = None
cssv.widget.head.padding = cssv.widget.padding

cssv.widget.body.padding = cssv.widget.padding
cssv.widget.body.color = cssv.color.grayDarker
cssv.widget.body.background = cssv.color.white

cssv.widget.foot.background = cssv.widget.body.background
cssv.widget.foot.color = cssv.widget.body.color

# Panel with default set to match the widget body values
cssv.panel.color = cssv.widget.body.color
cssv.panel.background = cssv.widget.body.background
cssv.panel.border.color = cssv.widget.border.color
cssv.panel.border.width = cssv.widget.border.width

class widget_header(mixin):
    
    def __call__(self, elem):
        elem['padding'] = cssv.widget.head.padding
        elem['overflow'] = 'hidden'
        css('h1,h2,h3,h4,h5',
            parent=elem,
            font_size=cssv.widget.head.font_size,
            font_weight=cssv.widget.head.font_weight,
            text_transform=cssv.widget.head.text_transform,
            line_height=cssv.widget.head.line_height,
            float='left',
            padding=0,
            margin=0,
            background='transparent')

################################################################ jQuery UI
css('body',
    css_include(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'media','ui.css')))

################################################################ CLICKABLE
clickable_default = lambda: clickable(\
            default=bcd(**cssv.clickable.default.params()),\
            hover=bcd(**cssv.clickable.hover.params()),\
            active=bcd(**cssv.clickable.active.params()))

css('.%s, .%s'%(classes.clickable,classes.button),
    clickable(default=bcd(**cssv.clickable.default.params()),
              hover=bcd(**cssv.clickable.hover.params()),
              active=bcd(**cssv.clickable.active.params())),
    radius(cssv.clickable.radius),
    css('a', text_decoration='none', color='inherit',
        font_weight='inherit', cursor='inherit'))
    
    
################################################################ WIDGET
css('.'+classes.widget,
    cssb('.bd',
         padding=cssv.widget.body.padding,
         overflow='hidden',
         display='block'),
    cssb('.ft',
         padding=cssv.widget.foot.padding,
         overflow='hidden')
)

cssb('.'+classes.widget_body,
     bcd(**cssv.widget.body.params()),
     border(color=cssv.widget.border.color,
            width=spacing(0, cssv.widget.border.width.right,
                          cssv.widget.border.width.bottom,
                          cssv.widget.border.width.left),
            style=cssv.widget.border.style),
     padding=cssv.widget.body.padding)
         
css('.'+classes.widget_head,
    bcd(**cssv.widget.head.params()),
    border(**cssv.widget.border.params()),
    widget_header(),
    css('.'+classes.edit_menu,
        line_height=cssv.widget.head.line_height),
    #css('a',
    #    clickable(default=bcd(background='transparent',
    #                          color=cssv.clickable.default.color,
    #                          text_decoration=cssv.clickable.default.text_decoration),
    #              hover=bcd(background='transparent',
    #                          color=cssv.clickable.hover.color,
    #                          text_decoration=cssv.clickable.hover.text_decoration),
    #              active=bcd(background='transparent',
    #                          color=cssv.clickable.active.color,
    #                          text_decoration=cssv.clickable.active.text_decoration)))
    )

cssb('.'+classes.widget_foot,
     bcd(**cssv.widget.foot.params()),
     border(color=cssv.widget.border.color,
            width=spacing(0, cssv.widget.border.width.right,
                          cssv.widget.border.width.bottom,
                          cssv.widget.border.width.left),
            style=cssv.widget.border.style),
     padding=cssv.widget.body.padding)
     
css('.'+classes.widget_body,
    overflow='hidden')
################################################################ PANEL
css('.'+classes.widget_body,
    cssa('.panel',
         bcd(**cssv.panel.params()),
         border(**cssv.panel.border.params())))

################################################################ RADIUS
css('.'+classes.corner_all,
    radius(cssv.body.radius))

radius_top = spacing(cssv.body.radius, cssv.body.radius, 0, 0)
radius_bottom = spacing(0, 0, cssv.body.radius, cssv.body.radius)
radius_left = spacing(cssv.body.radius, 0, 0, cssv.body.radius)
radius_right = spacing(0, cssv.body.radius, cssv.body.radius, 0)

css('.'+classes.corner_top, radius(radius_top))
css('.'+classes.corner_bottom, radius(radius_bottom))

################################################################ DRAGGABLE
css('.%s' % classes.draggable,
    cursor='move')