'''Top bar styling
'''
from djpcms.style import css, var
from . import defaults

variables.declare_from_module(defaults)


topbar_data = {
    'height': variables.topbar_height,
    'text_shadow': '0 1px 0 rgba(0, 0, 0, 0.5)',
    'subnav_radius': 6,
    'subnav_shadow': shadow('0 4px 8px rgba(0, 0, 0, 0.2)'),
    'subnav_padding': '4px 15px',
    #
    # Default Theme
    'gradient': gradient('#333','#222'), #background for container
    'color': '#BFBFBF',
    'subnav_color': '#808080',
    'color-hover': '#fff',
    'hover-background': '#333',
    'subnav-hover-background': '#222',
    'active-background': '#000',
    'active-color': '#fff',
    'brand_color': variables.topbar_brand_color,
    #
    # Fix data
    'margin-nav': 10,
    'subnav_width': '160px',
    'z-index': 10000,
    'overflow': 'visible',
    'min-width': variables.body_min_width,
    #
    # debug
    'dropdown_display': 'none' # set to block to see the subnavigation
}


def topbar(elem, data):
    height = variables.topbar_height
    data['height'] = '{0}px'.format(height)
    #
    #        calculate the anchor line height
    a1 = variables.topbar_height_padding
    a2 = a1+1
    anchor_line_height = height - a1 - a2
    if anchor_line_height < 10:
        raise valueError('Anchor line height in topbar is too low. Change the\
 "topbar_height" or "topbar_height_padding" values')
    data['anchor_padding'] = '{0}px {1}px {2}px'\
                .format(a1,variables.topbar_width_padding,a2)
    data['anchor_line_height'] = '{0}px'.format(anchor_line_height)
    #
    data['margin-nav'] = '{0}px'.format(data['margin-nav'])
    
    # subnav_radius
    r = data['subnav_radius']
    data['subnav_tolerance'] = r
    data['subnav_radius'] = radius('0 0 {0}px {0}px'.format(r))
    data['subnav2_radius'] = radius('0 {0}px {0}px 0'.format(r))
    data['subnav2_radius_secondary'] = radius('{0}px 0 0 {0}px'.format(r))
    data['list_subnav_padding'] = '{0}px 0'.format(r)
    return data


def topbar_brand(elem, data):
    size = variables.topbar_brand_font_size
    height = variables.topbar_height
    size = min(size,height)
    space = height - size
    if space:
        padding1 = space // 2
        padding2 = space - padding1
    else:
        padding1 = 0
        padding2 = 0
    data['font_size'] = '{0}px'.format(size)
    data['line_height'] = data['font_size']
    data['padding'] = '{0}px {2}px {1}px 0'.format(padding1,padding2,
                                                variables.topbar_brand_padding)
    return data

def topbar_form(elm, data):
    size = variables.topbar_brand_font_size
    size += 2*(variables.input_padding + variables.input_border_size)
    space = variables.topbar_height - size
    if space < 3:
        raise ValueError('Top bar to narrow to include the form')
    spaceh = (space // 2)
    space = space - spaceh
    if space == spaceh:
        space += 1
    data.update({'margin': '{0}px 0 0 0'.format(space)})
    return data
    
    
css('.topbar',
    process = topbar,
    **topbar_data)

css('a.brand',
    parent = '.topbar',
    process = topbar_brand,
    color = variables.topbar_brand_color,
    display = 'block',
    width = variables.topbar_brand_width,
    font_weight = variables.topbar_brand_font_weight,
    font_family = variables.topbar_brand_font_family)

css('form',
    parent = '.topbar',
    process = topbar_form)