from djpcms.style import *

# Control the size
cssv.topbar.height = px(40)
cssv.topbar.padding = spacing(px(10),px(10))
cssv.topbar.margin_horizontal = px(10)
cssv.topbar.secondary_with = px(160)
cssv.topbar.shadow = '0 4px 8px rgba(0, 0, 0, 0.2)'
cssv.topbar.radius = 0

# Color
cssv.topbar.background = ('v', '#333', '#222')
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
# brand
cssv.topbar.brand.color = '#ffffff'
cssv.topbar.brand.font_size = px(20)
cssv.topbar.brand.font_weight = None
cssv.topbar.brand.font_family = None
cssv.topbar.brand.padding = px(20)
cssv.topbar.brand.width = None


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
        gradient(tb.background)(elem)
        
        yield css('.nav',
                  horizontal_navigation(
                        default=bcd(**tb.default.params()),
                        active=bcd(**tb.active.params()),
                        hover=bcd(**tb.hover.params()),
                        height=height,
                        padding=tb.padding,
                        margin=cssv.topbar.margin_horizontal,
                        secondary_with=tb.secondary_with),
                  cssa('.secondary-nav',
                       horizontal_navigation(
                            float='right',
                            margin=cssv.topbar.margin_horizontal)))
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
        yield css('a.brand', parent = elem,
                  color = brand.color,
                  display = 'block',
                  width = brand.width,
                  font_weight = brand.font_weight,
                  font_family = brand.font_family,
                  font_size = size,
                  line_height = size,
                  padding = padding)
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


css('.topbar', topbar())
css('.topbar-fixed', fixtop(),
    gradient(cssv.topbar.background))
