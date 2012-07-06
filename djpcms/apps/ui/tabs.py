from .base import *

cssv.tabs.line_height = cssv.body.line_height
cssv.tabs.spacing = px(6)
cssv.tabs.padding = spacing(px(6), px(10), 0)
cssv.tabs.content.padding = spacing(px(15), px(10), px(6))
cssv.tabs.border_color = cssv.body.border_color
cssv.tabs.default.color = cssv.link.default.color
cssv.tabs.active.background = cssv.body.background
cssv.tabs.active.color = cssv.body.color
cssv.tabs.hover.background = lazy(color.lighten, cssv.tabs.border_color, 5)

cssv.accordion.spacing = px(2)


#################################################    TABS
css('.'+classes.tabs,
    cssb('ul',
        clearfix(),
        radius(radius_top),
        cssb('li',
             cssa('.%s' % classes.clickable, border_bottom='none'),
             cssb('a',
                  radius(radius_top),
                  display='block',
                  line_height=cssv.tabs.line_height,
                  padding=spacing(px(8),px(12))),
             float='left',
             line_height=cssv.tabs.line_height,
             margin_right=cssv.tabs.spacing),
        # pills
        cssa('pills'),
        #
        padding=cssv.tabs.padding,
        border_bottom='none'),
    cssb('div',
         border(color=cssv.widget.head.border.color,
                width=spacing(0,px(1),px(1))),
         padding=cssv.tabs.content.padding),
    padding=0,
    )

css('.ui-tabs-hide',
    display='none')


#################################################    ACCORDION
css('.ui-accordion-container',
    cssb('.'+classes.clickable,
         cssa(':first-child', margin_top=0),
         margin_top=cssv.accordion.spacing),
    css('.ui-accordion-header',
        widget_header()),
    border='none')
