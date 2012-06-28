from .base import *

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

#################################################    TABS
css('.'+classes.tabs,
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
