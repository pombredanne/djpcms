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

# body
cssv.body.background = cssv.color.white
cssv.body.color = cssv.color.grayDarker
cssv.body.font_family = "Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif"
cssv.body.font_size = px(14)
cssv.body.line_height = px(18)
cssv.body.min_width = px(960)
cssv.body.text_align = 'left'

# Links
cssv.link.weight = 'normal'
# default
cssv.link.default.color = '#08c'
cssv.link.default.background = None
cssv.link.default.text_decoration = 'none'
cssv.link.default.text_shadow = None
# hover
cssv.link.hover.color = lazy(color.darken, cssv.link.default.color, 15)
cssv.link.hover.background = None
cssv.link.hover.text_decoration = 'none'
cssv.link.hover.text_shadow = None

cssv.edit.background = cssv.color.black
cssv.edit.color = cssv.color.white

################################################# BODY
css('body',
    background = cssv.body.background,
    color = cssv.body.color,
    font_family = cssv.body.font_family,
    font_size = cssv.body.font_size,
    min_width = cssv.body.min_width,
    line_height = cssv.body.line_height,
    text_align = cssv.body.text_align)

################################################# DEFAULT CLICKABLE ANCHORS
css('a:link',
    clickable(**cssv.link.params()),
    weight = cssv.link.weight
)

################################################# GRID GENERATORS
grid(12, 60, 20)
fluidgrid(12)

################################################# EDIT PAGE PANEL
css('.edit-panel',
    gradient(cssv.edit.background),
    position='fixed',
    top=0,
    right=0,
    left=0)