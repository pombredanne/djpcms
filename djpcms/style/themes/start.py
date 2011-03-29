#
#   START THEME from jQuery UI
#
from medplate import CssTheme

theme_name = 'start'

highlight = {'background':'#F8DA4E',
             'color':'#915608',
             'border_color': ' #FCD113'}

CssTheme('body',
         theme_name,
         data = {'color':'#222222',
                 'highlight': highlight}
         )

CssTheme('widget-anchor',
         theme_name,
         data = {
                   'text_decoration': 'none',
                   'weight':'normal',
                   'color':'#026890',
                   'color_hover':'#6eac2c',
                   }
         )

CssTheme('breadcrumbs',
         theme_name,
         data = {})


CssTheme('bodyedit',
         theme_name,
         data = {
                 'background': '#f5f5f5',
                 'color': '#000',
                 })

CssTheme('box',
         theme_name,
         data = {})

CssTheme('flatbox',
         theme_name,
         data = {
            'background':'#ffffff',
            'border':'1px solid #4297d7'
                 })


CssTheme('tablesorter',
         theme_name,
         data = {
                 'head_border_color':'#fff',
                 'body_border_color':'#a6c9e2',
                 'odd_background_color':'#dbebeb',
                 'row_hover_background':'#d0e5f5',
                 })


CssTheme('nav',
         theme_name,
         data = {
                'main_text_shadow': '0 2px 2px rgba(0, 0, 0, 0.5)',
                'secondary_text_shadow': 'none',
                # SHADOW OF DROP DOWN MENU
                'secondary_border_color':'#b4b4b4',
                'drop_down_shadow': '10px 10px 5px rgba(0,0,0, .5)',
                'font_weight': 'bold',
                'color': '#E7E5E5',
                'background':'transparent',
                'hover_background':'#79c9ec',
                'secondary_hover_background':'#c2c2c2',
                'selected_background':'#dcdcdc',
                'hover_color': '#444',
                'selected_color':'#444',
                'padding': '2px 0',     # Padding for outer ul
                'height': '30px',
                'inner_radius': '10px',
                'list_margin': '0 5px',
                'anchor_padding': '0 20px',
                'radius': '14px'
               },
         )

CssTheme('edit_plugin_body',
         theme_name,
         data = {
                 'background':'#BAE28D'
                 }
)


CssTheme('field-widget-input',
         theme_name,
         data = {
                 'background':'#ffffff',
                 'border':'1px solid #a6c9e2'
                 }
)