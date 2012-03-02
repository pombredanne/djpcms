from .pagelayout import style
from .topbar import style
from .uniforms import style
from .table import style
from .bootstrap import style
from medplate import variables



############################################################
#    START THEME
start = variables.theme_setter('start')
start.table_odd_background_color = '#f2f2f2'
start.table_even_background_color = 'transparent'
start.table_even_sort_background = '#fcefa1'
start.table_odd_sort_background = '#f7eeb5'


############################################################
#    SIRO THEME
siro = variables.theme_setter('siro')
siro.table_odd_background_color = '#f2f2f2'
siro.table_even_background_color = 'transparent'
siro.table_even_sort_background = '#fbec88'
siro.table_odd_sort_background = '#f0e7ad'