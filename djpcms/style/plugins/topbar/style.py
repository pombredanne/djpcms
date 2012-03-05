'''Top bar styling
'''
from djpcms.style import css, mixin, cssv, gradient, shadow
from . import defaults

cssv.declare_from_module(defaults)


topbar_data = {
    'subnav_radius': 6,
    #'subnav_shadow': shadow('0 4px 8px rgba(0, 0, 0, 0.2)'),
    'subnav_padding': '4px 15px',
    #
    # Default Theme
    'subnav_color': '#808080',
    'color-hover': '#fff',
    'hover-background': '#333',
    'subnav-hover-background': '#222',
    'active-background': '#000',
    'active-color': '#fff',
    #
    'subnav_width': '160px',
    #
    # debug
    'dropdown_display': 'none' # set to block to see the subnavigation
}

class topbar(mixin):
    
    def __call__(self):
        height = cssv.topbar_height
        a1 = cssv.topbar_height_padding
        a2 = a1+1
        anchor_line_height = height - a1 - a2
        if anchor_line_height < 10:
            raise valueError('Anchor line height in topbar is too low.\
 Change the "topbar_height" or "topbar_height_padding" values')
            
        container = shadow(
                        gradient(
                            css('.topbar',
                                height = '{0}px'.format(height),
                                z_index = 10000,
                                overflow = 'visible',
                                text_shadow = cssv.topbar_text_shadow,
                                min_width = cssv.body_min_width
                                ),
                            cssv.topbar_gradient
                            ),
                        cssv.topbar_shadow).css()
        nav = css('.nav',
                  css('ul', position = 'absolute'),
                  css('li', position = 'relative'),
                  parent = container,
                  display = 'block',
                  float = 'left',
                  position = 'relative',
                  margin = '0 {0}px 0 0'.format(cssv.topbar_horizontal_margin))
        yield container
        yield nav
        yield css('.nav.secondary-nav', parent = container,
                  float = 'right',
                  margin = '0 0 0 {0}px'.format(cssv.topbar_horizontal_margin))
        yield css('.nav > li', parent = container,
                  display = 'block', float = 'left')
        yield css('li.active', parent = nav,
                  background = cssv.topbar_active_background)
        #
        # topbar anchor
        yield css('a', parent = nav,
                  float = 'none',
                  display = 'inline-block',
                  text_decoration = 'none',
                  padding = '{0}px {1}px {2}px'\
                      .format(a1,cssv.topbar_width_padding,a2),
                  line_height = '{0}px'.format(anchor_line_height),
                  color = cssv.topbar_color)
        #
        # branding
        size = min(cssv.topbar_brand_font_size, height)
        space = height - size
        if space:
            padding1 = space // 2
            padding2 = space - padding1
        else:
            padding1 = 0
            padding2 = 0
        yield css('a.brand', parent = container,
                  color = cssv.topbar_brand_color,
                  display = 'block',
                  width = cssv.topbar_brand_width,
                  font_weight = cssv.topbar_brand_font_weight,
                  font_family = cssv.topbar_brand_font_family,
                  font_size = '{0}px'.format(size),
                  line_height = '{0}px'.format(size),
                  padding = '{0}px {2}px {1}px 0'.format(padding1,padding2,
                                            cssv.topbar_brand_padding))
        #
        # form
        size = cssv.topbar_brand_font_size
        size += 2*(cssv.input_padding + cssv.input_border_size)
        space = cssv.topbar_height - size
        if space < 3:
            raise ValueError('Top bar to narrow to include the form')
        spaceh = (space // 2)
        space = space - spaceh
        if space == spaceh:
            space += 1
        yield css('form', parent = 'container',
                  margin = '{0}px 0 0 0'.format(space))

        # subnav_radius
        r = data['subnav_radius']
        data['subnav_tolerance'] = r
        data['subnav_radius'] = radius('0 0 {0}px {0}px'.format(r))
        data['subnav2_radius'] = radius('0 {0}px {0}px 0'.format(r))
        data['subnav2_radius_secondary'] = radius('{0}px 0 0 {0}px'.format(r))
        data['list_subnav_padding'] = '{0}px 0'.format(r)


topbar().css()