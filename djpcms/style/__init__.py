import os

import djpcms

from .api import *

################################################################################
##    DEFINE THE BASE STYLE VARIABLES
################################################################################

# Grey scale
cssv.color.black = color('000')
cssv.color.grayDarker = color('222')
cssv.color.grayDark = color('333')
cssv.color.gray = color('555')
cssv.color.grayLight = color('999')
cssv.color.grayLighter = color('e6e6e6')
cssv.color.white = color('fff')

# Global body variable
cssv.body.background = cssv.color.white
cssv.body.color = cssv.color.grayDarker
cssv.body.border_color = cssv.color.grayLighter
cssv.body.font_family = "Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif"
cssv.body.font_size = px(14)
cssv.body.line_height = px(18)
cssv.body.min_width = px(960)
cssv.body.text_align = 'left'
cssv.body.radius = px(0)

cssv.header.background = cssv.color.grayLight
# Inputs
cssv.input.placeholder_color = cssv.color.grayLight

# Headings
cssv.heading.font_weight = 'bold'
cssv.heading.h3.font_size = lazy(lambda: 1.3*cssv.body.font_size)
cssv.heading.h3.line_height = lazy(lambda: 1.5*cssv.body.line_height)
cssv.paragraph.margin = spacing(0,0,px(9))

# Links
cssv.link.font_weight = 'normal'
# default
cssv.link.default.color = '#08c'
cssv.link.default.background = None
cssv.link.default.text_decoration = 'none'
cssv.link.default.text_shadow = None
# hover
cssv.link.hover.color = lazy(color.darken, cssv.link.default.color, 15)
cssv.link.hover.background = None
cssv.link.hover.text_decoration = 'underline'
cssv.link.hover.text_shadow = None

# Margins
cssv.block.margin_bottom = px(20)

# edit page panel
cssv.edit.background = cssv.color.grayDarker
cssv.edit.border_color = cssv.edit.background 
cssv.edit.color = cssv.color.white
cssv.edit.font_size = pc(90)
cssv.edit.link.hover.text_decoration = 'none'
cssv.edit.link.default.color = cssv.color.grayLighter
cssv.edit.link.hover.color = lazy(color.darken,
                                  cssv.edit.link.default.color, 15)

################################################# BODY
css('body',
    css_include(os.path.join(djpcms.PACKAGE_DIR,'media','reset.css')),
    grid(12, 60, 20),
    gridfluid(12),
    gridfluid(24),
    background = cssv.body.background,
    color = cssv.body.color,
    font_family = cssv.body.font_family,
    font_size = cssv.body.font_size,
    min_width = cssv.body.min_width,
    line_height = cssv.body.line_height,
    text_align = cssv.body.text_align)

################################################# TOPOGRAPHY
css('h1,h2,h3,h4,h5,h6',
    font_weight=cssv.heading.font_weight,
    text_rendering='optimizelegibility',
    margin=0)
css('h1',
    font_size=lazy(lambda: 2*cssv.body.font_size),
    line_height=lazy(lambda: 2*cssv.body.line_height))
css('h2',
    font_size=lazy(lambda: 1.6*cssv.body.font_size),
    line_height=lazy(lambda: 1.8*cssv.body.line_height))
css('h3',
    font_size=cssv.heading.h3.font_size,
    line_height=cssv.heading.h3.line_height)
css('h4',
    font_size=lazy(lambda: 1.2*cssv.body.font_size),
    line_height=lazy(lambda: 1.4*cssv.body.line_height))
css('h5',
    font_size=lazy(lambda: cssv.body.font_size),
    line_height=lazy(lambda: cssv.body.line_height))
css('h6',
    font_size=lazy(lambda: 0.9*cssv.body.font_size),
    line_height=lazy(lambda: cssv.body.line_height),
    text_transform='uppercase')
css('p',
    cssa(':last-child',
         margin=0),
    margin=cssv.paragraph.margin)

################################################# DEFAULT CLICKABLE ANCHORS
css('a',
    clickable(**cssv.link.params()),
    font_weight=cssv.link.font_weight
)

css('input',
    placeholder(cssv.input.placeholder_color))

css('.cms-block',
    clearfix(),
    margin_bottom=cssv.block.margin_bottom)

css('.ui-widget.box',
    cssa('.edit-block',
         cssb('.ui-widget-head,.ui-widget-body',
              gradient(cssv.edit.background),
              color=cssv.edit.color),
         css('.cms-block',
             margin_bottom=0),
         border_color=cssv.edit.border_color))

################################################# EDIT PAGE PANEL
css('#page-edit-page',
    #fixtop(),
    css('a',clickable(**cssv.edit.link.params())),
    gradient(cssv.edit.background),
    color=cssv.edit.color,
    font_size=cssv.edit.font_size)
