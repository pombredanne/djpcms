'''Top bar styling
'''
from djpcms.apps.nav import topbar_class, topbar_fixed

from pycss import *

from . import defaults

cssv.declare_from_module(defaults)


topbar_data = {
    'subnav_radius': 6,
    #'subnav_shadow': shadow('0 4px 8px rgba(0, 0, 0, 0.2)'),
    'subnav_padding': '4px 15px',
    #
    # Default Theme
    'subnav_color': '#808080',
    'subnav-hover-background': '#222',
    'active-background': '#000',
    'active-color': '#fff',
    #
    'subnav_width': '160px',
    #
    # debug
    'dropdown_display': 'none' # set to block to see the subnavigation
}

class topbar(generator):
    
    def __init__(self, topbar_class ='topbar'):
        self.topbar_class = topbar_class
        
    def __call__(self):
        height = cssv.topbar_height
        a1 = cssv.topbar_height_padding
        a2 = a1+1
        anchor_line_height = height - a1 - a2
        if anchor_line_height < 10:
            raise valueError('Anchor line height in topbar is too low.\
 Change the "topbar_height" or "topbar_height_padding" values')
        
        # The container for the top bar
        container = css('.'+self.topbar_class,
                        shadow(cssv.topbar_shadow),
                        gradient(cssv.topbar_background),
                        height = '{0}px'.format(height),
                        z_index = 10000,
                        overflow = 'visible',
                        text_shadow = cssv.topbar_text_shadow,
                        min_width = cssv.body_min_width)
        hm = cssv.topbar_horizontal_margin
        nav = css('.nav',
                  css('.secondary-nav',
                      float = 'right',
                      margin = lambda : '0 0 0 {0}px'.format(hm)),
                  cssb('li',
                       cssa('hover', background=cssv.topbar_background_hover),
                       display = 'block', float = 'left'),
                  css('ul',
                      position = 'absolute',
                      display = 'none',
                      background = cssv.topbar_background_hover),
                  css('li',
                      cssc('.active',
                           background=cssv.topbar_background_active,
                           color=cssv.topbar_color_active),
                      position = 'relative'),
                  parent = container,
                  display = 'block',
                  float = 'left',
                  position = 'relative',
                  margin = lambda : '0 {0}px 0 0'.format(
                                                cssv.topbar_horizontal_margin))
        yield container
        yield nav
        #
        # topbar anchor
        yield css('a',
                  cssa('hover', color = cssv.topbar_color_hover),
                  parent = nav,
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
        yield css('form',
                  parent = container,
                  margin = '{0}px 0 0 0'.format(space))

        # subnav_radius
        #r = data['subnav_radius']
        #data['subnav_tolerance'] = r
        #data['subnav_radius'] = radius('0 0 {0}px {0}px'.format(r))
        #data['subnav2_radius'] = radius('0 {0}px {0}px 0'.format(r))
        #data['subnav2_radius_secondary'] = radius('{0}px 0 0 {0}px'.format(r))
        #data['list_subnav_padding'] = '{0}px 0'.format(r)


################################################# TOPBAR
topbar()
css('.'+topbar_fixed, fixtop())
