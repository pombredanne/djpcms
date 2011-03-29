#
#   START THEME from jQuery UI
#
from copy import deepcopy

from medplate import CssTheme
from .smooth import make_theme, smooth

theme_name = 'start'

start = deepcopy(smooth)

start['flatbox']['border'] = '1px solid #4297d7'

make_theme(theme_name,start)

#highlight = {'background':'#F8DA4E',
#             'color':'#915608',
#             'border_color': ' #FCD113'}


