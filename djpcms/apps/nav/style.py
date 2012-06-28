'''Top bar styling
'''
from djpcms.media.style import *

from . import classes

# Control the size
cssv.topbar.height = px(40)
cssv.topbar.padding = spacing(px(10),px(10))
cssv.topbar.margin_horizontal = px(10)
cssv.topbar.secondary_width = px(160)
cssv.topbar.shadow = '0 4px 8px rgba(0, 0, 0, 0.2)'
cssv.topbar.radius = 0

# Main navigation
# Color
cssv.topbar.default.background = ('v', '#333', '#222')
cssv.topbar.default.color = '#BFBFBF'
cssv.topbar.default.text_decoration = 'none'
cssv.topbar.default.text_shadow = '0 1px 0 rgba(0, 0, 0, 0.5)'
# hover
cssv.topbar.hover.background = color('333')
cssv.topbar.hover.color = color('fff')
cssv.topbar.hover.text_decoration = cssv.topbar.default.text_decoration
cssv.topbar.hover.text_shadow = cssv.topbar.default.text_shadow
# active
cssv.topbar.active.background = cssv.color.black
cssv.topbar.active.color = cssv.color.white
cssv.topbar.active.text_decoration = cssv.topbar.hover.text_decoration
cssv.topbar.active.text_shadow = cssv.topbar.hover.text_shadow

# Subnavigation
#Color
cssv.topbar.secondary_default.background = cssv.topbar.hover.background
cssv.topbar.secondary_default.color = '#BFBFBF'
cssv.topbar.secondary_default.text_decoration = 'none'
cssv.topbar.secondary_default.text_shadow = '0 1px 0 rgba(0, 0, 0, 0.5)'
# hover
cssv.topbar.secondary_hover.background = color('222')
cssv.topbar.secondary_hover.color = color('fff')
cssv.topbar.secondary_hover.text_decoration = cssv.topbar.secondary_default.text_decoration
cssv.topbar.secondary_hover.text_shadow = cssv.topbar.secondary_default.text_shadow
# active
cssv.topbar.secondary_active.background = cssv.color.black
cssv.topbar.secondary_active.color = cssv.color.white
cssv.topbar.secondary_active.text_decoration = cssv.topbar.secondary_hover.text_decoration
cssv.topbar.secondary_active.text_shadow = cssv.topbar.secondary_hover.text_shadow
# brand
cssv.topbar.brand.color = '#ffffff'
cssv.topbar.brand.font_size = px(20)
cssv.topbar.brand.font_weight = None
cssv.topbar.brand.font_family = None
cssv.topbar.brand.padding = px(20)
cssv.topbar.brand.width = None

# BREADCRUMBS
cssv.breadcrumbs.font_size = pc(130)

class topbar(mixin):
    
    def __call__(self, elem):
        tb = cssv.topbar
        height = tb.height
        elem['height'] = height
        elem['z_index'] = 10000
        elem['overflow'] = 'visible'
        elem['margin-top'] = 0
        elem['margin-bottom'] = 0
        elem['border'] = 'none'
        gradient(tb.default.background)(elem)
        
        css('.nav',
            horizontal_navigation(
                default=bcd(**tb.default.params()),
                active=bcd(**tb.active.params()),
                hover=bcd(**tb.hover.params()),
                secondary_default=bcd(**tb.secondary_default.params()),
                secondary_active=bcd(**tb.secondary_active.params()),
                secondary_hover=bcd(**tb.secondary_hover.params()),
                height=height,
                padding=tb.padding,
                margin=cssv.topbar.margin_horizontal,
                secondary_width=tb.secondary_width),
            cssa('.secondary-nav',
                 horizontal_navigation(
                    float='right',
                    margin=cssv.topbar.margin_horizontal)),
            parent=elem)
        # branding
        brand = tb.brand
        padding = spacing(brand.padding)
        size = min(brand.font_size, height)
        space = height - size
        if space:
            padding1 = space // 2
            padding2 = space - padding1
        else:
            padding1 = 0
            padding2 = 0
        padding = spacing(padding1,padding.right,padding2,padding.left)
        css('a.brand',
            color = brand.color,
            display = 'block',
            width = brand.width,
            font_weight = brand.font_weight,
            font_family = brand.font_family,
            font_size = size,
            line_height = size,
            padding = padding,
            parent=elem)
        #
        # form
        #size += 2*(cssv.input.padding + cssv.input.border_size)
        #space = cssv.topbar_height - size
        #if space < 3:
        #    raise ValueError('Top bar to narrow to include the form')
        #spaceh = (space // 2)
        #space = space - spaceh
        #if space == spaceh:
        #    space += 1
        #yield css('form',
        #          parent = elem,
        #          margin = '{0}px 0 0 0'.format(space))


css('.'+classes.topbar, topbar())
css('.'+classes.topbar_fixed, fixtop(),
    gradient(cssv.topbar.default.background))
cssa('.editable',
     css('.topbar-fixed', unfixtop()))


css('.'+classes.breadcrumbs,
    css('ul, ul li', list_style='none', display='inline'),
    font_size=cssv.breadcrumbs.font_size)
