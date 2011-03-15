from medplate import CssTheme, jQueryTheme

theme_name = 'siro'

jQueryTheme(theme_name,'redmond')

CssTheme('bodyedit',
         theme_name,
         data = {
                 'background': '#f5f8f9',
                 }
)

CssTheme('tablesorter',
         theme_name,
         data = {
            'odd_background_color':'#dfeffc',
            'row_hover_background':'#d0e5f5',
        }
)