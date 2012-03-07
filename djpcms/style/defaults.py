# Default variables for djpcms.style
from pycss import color, cssv, lazy

# body
body_background = '#ffffff'
body_color = '#222222'
body_font_family = "Helvetica,Arial,'Liberation Sans',FreeSans,sans-serif"
body_font_size = 14
body_line_height = '18px'
body_min_width = '960px'
body_text_align = 'left'

# Corner radius
corner_all = '5px'
# Padding and border for inputs
input_padding = 3
input_border_size = 1

########################### LINKS
link_weight = 'normal'
link_color = '#08c'
link_background = None
link_decoration = 'none'
link_color_hover = lazy(lambda: color.darken(cssv.link_color, 15))
link_background_hover = None
link_decoration_hover = 'none'

# disabled elements
disabled_opacity = 0.7
disabled_cursor = 'not-allowed'

#blocks
block_margin = 15

# widget
widget_hd_padding = '6px 5px'
widget_bd_padding = '5px 5px'
widget_ft_padding = '5px 5px'
widget_hd_fontsize = '110%'
widget_hd_fontweight = 'bold'

# dragging
dragging_width = '200px'

########################### DEFINITION LIST
definition_list_opacity = 0.8

