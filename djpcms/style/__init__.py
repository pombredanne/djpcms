from .pycss import *
from . import defaults
from .mixins import *
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

################################################# GRID
grid(12,60,20).css()
fluidgrid(12).css()

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
