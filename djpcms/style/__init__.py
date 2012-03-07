try:
    from pycss import *
except ImportError:
    import sys
    import os
    sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0],
                                 '_pycss'))
    from pycss import *
from . import defaults

cssv.declare_from_module(defaults)

################################################# BODY
css('body',
    background = cssv.body_background,
    color = cssv.body_color,
    font_family = cssv.body_font_family,
    font_size = cssv.body_font_size,
    min_width = cssv.body_min_width,
    line_height = cssv.body_line_height,
    text_align = cssv.body_text_align)

################################################# DEFAULT ANCHORS
css('a',
    cssa('link,visited', color = cssv.link_color),
    cssa('link:hover',
         color = cssv.link_color_hover,
         text_decoration = cssv.link_decoration_hover,
         background = cssv.link_background_hover),
    color = cssv.link_color,
    background = cssv.link_background,
    weight = cssv.link_weight,
    text_decoration = cssv.link_decoration,
)

################################################# GRID GENERATORS
grid(12,60,20)
fluidgrid(12)

################################################# DJPCMS BOX
css('.djpcms-html-box',
    css('.collapsed > .bd', display = 'none'))

################################################# WIDGET
css('.widget',
    css('.hd',
        css('h1,h2,h3,h4,h5',
            font_size = cssv.widget_hd_fontsize,
            font_weight = cssv.widget_hd_fontweight,
            float = 'left',
            padding = 0,
            margin = 0,
            background = 'transparent'
        ),
        padding = cssv.widget_hd_padding,
        overflow='hidden',
    ),
    css('.bd',
        padding = cssv.widget_bd_padding,
        overflow = 'hidden',
        border = 'none'),
    css('.ft',
        padding = cssv.widget_ft_padding,
        overflow = 'hidden',
        border = 'none')
)

################################################# OBJECT DEFINITIONS
css('.object-definition',
    css('dl',
        cssa(':first-child', margin_top = 0),
        css('dt',
            opacity = cssv.definition_list_opacity,
            float = 'left', width = '40%', margin = 0),
        css('dd', margin = 0)
        ),
    cssc('.w20 dl dt', width = '20%'),
    cssc('.w40 dl dt', width = '40%'),
    cssc('.w50 dl dt', width = '50%'),
    overflow = 'hidden',
    margin = '5px 0 0')
