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

# edit page panel
cssv.edit.background = cssv.color.black
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

################################################# DEFAULT CLICKABLE ANCHORS
css('a',
    clickable(**cssv.link.params()),
    font_weight=cssv.link.font_weight
)

################################################# EDIT PAGE PANEL
css('#page-edit-page',
    #fixtop(),
    css('a',clickable(**cssv.edit.link.params())),
    gradient(cssv.edit.background),
    color=cssv.edit.color,
    font_size=cssv.edit.font_size)