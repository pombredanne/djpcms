from .pycss import *
from . import defaults
from .mixins import *
vars.declare_from_module(defaults)

################################################# BODY
css('body',
    background = vars.body_background,
    color = vars.body_color,
    font_family = vars.body_font_family,
    font_size = vars.body_font_size,
    min_width = vars.body_min_width,
    line_height = vars.body_line_height,
    text_align = vars.body_text_align)

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
            font_size = vars.widget_hd_fontsize,
            font_weight = vars.widget_hd_fontweight,
            float = 'left',
            padding = 0,
            margin = 0,
            background = 'transparent'
        ),
        padding = vars.widget_hd_padding,
        overflow='hidden',
    ),
    css('.bd',
        padding = vars.widget_bd_padding,
        overflow = 'hidden',
        border = 'none'),
    css('.ft',
        padding = vars.widget_ft_padding,
        overflow = 'hidden',
        border = 'none')
)
