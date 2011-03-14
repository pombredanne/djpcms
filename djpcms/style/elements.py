


def horizontal_navigation(data):
    '''Calculate css for horizontal navigation'''
    align = data.pop('align','left')
    if align == 'left':
        data['nav_float'] = 'left'
    elif align == 'right':
        data['nav_float'] = 'right'
    else:
        data['li_display'] = 'inline'
        data['overflow'] = 'hidden'
        data['display'] = 'inline'
    anchor_horizontal_padding = data.pop('anchor_horizontal_padding',20)
    secondary_anchor_width = data.pop('secondary_anchor_width',100)
    secondary_border_with = data.pop('secondary_border_with',0)
    data['anchor_padding'] = '0 {0}px'.format(anchor_horizontal_padding)
    wp  = 2*anchor_horizontal_padding+secondary_anchor_width
    l3p = wp+0*secondary_border_with
    data['secondary_width'] = '{0}px'.format(secondary_anchor_width)
    data['left3plus'] = '{0}px'.format(l3p)
    data['top3plus'] = '-{0}px'.format(secondary_border_with)
    border_color = data.pop('secondary_border_color',None)
    if secondary_border_with:
        data['secondary_border'] = '{0}px solid {1}'.format(secondary_border_with,
                                                            border_color)
    return data


def object_definition(data):
    left = data['left_width']
    right = 100 - left
    data['left_width'] = '{0}%'.format(left)
    data['right_width'] = '{0}%'.format(right)
    return data