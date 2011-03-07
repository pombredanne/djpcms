#
#   START THEME
#
from medplate import CssTheme

theme_name = 'start'

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
         data = {
                 'background':'#aaa'
                 })


CssTheme('tablesorter',
         theme_name,
         data = {
                 'head_border_color':'#fff',
                 'body_border_color':'#a6c9e2',
                 'odd_background_color':'#dbebeb'
                 })