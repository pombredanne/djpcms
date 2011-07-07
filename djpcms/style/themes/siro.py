from medplate import CssTheme, jQueryTheme
from .start import start, make_theme, deepcopy

theme_name = 'siro'
jQueryTheme(theme_name,'redmond')

blue = '#2B4E72'    # Dark blue
border = '#A6C9E2'

siro = deepcopy(start)


siro.update({
    # datatable
    'datatable': {'odd_background_color':'#f2f2f2',
                  'even_sort_background':'#fbec88',
                  'odd_sort_background':'#f0e7ad'},
})

siro['breadcrumbs']['color'] = blue
siro['flatbox']['border'] = '1px solid '+border
siro['edit_plugin_body']['background'] = '#dfeffc'


siro['nav'] = {'main_text_shadow': '0 2px 2px rgba(0, 0, 0, 0.5)',
               'secondary_text_shadow': 'none',
               'font_weight': 'bold',
               'secondary_border_color':'#b4b4b4',
               'drop_down_shadow': '10px 10px 5px rgba(0,0,0, .5)',
               'color': '#E7E5E5',
               'hover_background':'#ccc',
               'hover_color': '#444',
               #
               # Secondary lists
               'secondary_hover_background':'#A6C9E2',
               'secondary_active_background':'#FAD42E',
               'secondary_active_color':'#353432',
               'selected_color':'#444',
               'list_margin': '0 5px',
               'hover_background':blue,
             }


make_theme(theme_name,siro)

CssTheme('tablerelated-legend',
         theme_name,
         data = {
            'background':'#f2f2f2'
    }
)
