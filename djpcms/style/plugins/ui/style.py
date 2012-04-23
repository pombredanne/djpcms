from djpcms.style import *

cssv.panel.background = cssv.color.grayLighter
cssv.panel.border_color = color(RGBA(0,0,0,0.05))
cssv.panel.border_width = px(1)
cssv.panel.padding = spacing(px(6))

cssv.widget.head.background = cssv.panel.background
cssv.widget.head.font_size = cssv.heading.h3.font_size
cssv.widget.head.line_height = cssv.heading.h3.line_height
cssv.widget.head.font_weight = cssv.head.font_weight
cssv.widget.head.text_transform = 'none'
cssv.widget.padding = cssv.panel.padding
cssv.widget.head.padding = cssv.widget.padding
cssv.widget.bd.padding = cssv.widget.padding
cssv.widget.ft.padding = cssv.widget.padding

cssv.tabs.line_height = cssv.body.line_height
cssv.tabs.radius = cssv.body.radius
cssv.tabs.border_color = cssv.body.border_color
cssv.tabs.default.color = cssv.link.default.color
cssv.tabs.active.background = cssv.body.background
cssv.tabs.active.color = cssv.body.color
cssv.tabs.hover.background = lazy(color.lighten, cssv.tabs.border_color, 5)

def tabs_border():
    color = cssv.tabs.border_color
    return '{0} {0} transparent'.format(color)

corner_top = lambda: spacing(cssv.body.radius, cssv.body.radius, 0, 0)
    
    
css('.ui-corner-all', radius(cssv.body.radius))

css('.ui-corner-top',
    radius(lazy(corner_top)))

css('.ui-widget-head',
    #radius(lazy(corner_top)),
    gradient(cssv.widget.head.background),
    css('h1,h2,h3,h4,h5',
        font_size=cssv.widget.head.font_size,
        font_weight=cssv.widget.head.font_weight,
        text_transform=cssv.widget.head.text_transform,
        line_height=cssv.widget.head.line_height,
        float = 'left',
        padding = 0,
        margin = 0,
        background = 'transparent'
    ),
    css('.edit-menu',
        line_height=cssv.widget.head.line_height),
    padding=cssv.widget.head.padding,
    overflow='hidden')

css('.ui-widget',
    cssb('.hd',
         padding_top=0,
         padding_bottom=0),
    cssb('.bd',
         padding=cssv.widget.bd.padding,
         overflow='hidden',
         border='none',
         display='block'),
    cssb('.ft',
         padding=cssv.widget.ft.padding,
         overflow='hidden',
         border='none')
)

################################################# BOX and PANEL
css('.panel,.box',
    border_style='solid',
    border_width=cssv.panel.border_width,
    border_color=cssv.panel.border_color)

css('.box',
    cssa('.flat',
         css('.ui-widget-head',
             backgroud='transparent')))

css('.panel',
    gradient(cssv.panel.background),
    padding=cssv.panel.padding)

css('.ui-tabs',
    css('ul',
        clearfix(),
        # tab list
        cssb('li',
             cssb('a',
                  color=cssv.tabs.default.color,
                  display='block'),
             float='left',
             line_height=cssv.tabs.line_height),
        # tabs
        cssa('.tabs',
             cssb('li',
                  cssb('a',
                       cssa(':hover',
                            gradient(cssv.tabs.hover.background),
                            text_decoration='none'),
                       radius(spacing(cssv.tabs.radius, cssv.tabs.radius, 0, 0)),
                       border='1px solid transparent',
                       line_height=cssv.tabs.line_height,
                       padding=spacing(px(8),px(12))),
                  cssa('.ui-state-active',
                       cssb('a, a:hover',
                            gradient(cssv.tabs.active.background),
                            color=cssv.tabs.active.color,
                            border_color= lazy(tabs_border),
                            text_decoration='none')),
                  margin_bottom=px(-1)),
             border_bottom='1px solid',
             border_color=cssv.tabs.border_color),
        # pills
        cssa('pills'),
        #
        margin_bottom=cssv.tabs.line_height),
    cssb('div',
         margin_bottom=cssv.tabs.line_height)
    )

css('.ui-tabs-hide',
    display='none')


css('.ui-accordion-container',
    cssb('.ui-widget-head',
         cssa(':first-child', margin_top=0),
         margin_top=px(1)),
    border='none')
