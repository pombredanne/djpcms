from .templates import *
from . import defaults
vars.declare_from_module(defaults)

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