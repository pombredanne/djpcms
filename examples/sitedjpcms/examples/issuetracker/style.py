#
# Script for generating style-sheet
from medplate import CssContext, CssBody, CssTheme
from djpcms.style import boxradius

root = CssBody(data = {'text_shadow': '4px 4px 4px #ddd'})


CssTheme('nav',
         'smooth',
         data = {'text_align':'center',
                 'hover_background':'#ccc',
                 'selected_background':'#33789C',
                 'selected_color':'#fff',
                 'padding': '5px 0',
                 'height': '30px',
                 'inner_radius': '10px',
                 'secondary_width': '100px',
                 'anchor_padding': '0 10px',
                 'position':'relative !important'})


#context.tags.update({'line_height':'1.4em'})

#context.breadcrumbs.update({'margin':'0 0 10px 0'})

# Style box
boxradius(7)
#context.box.bd.update({'background':'#fff',
#                       'radius_top_right':'0px',
#                       'radius_top_left':'0px'})
#context.box.ft.update({'background':'#fff',
#                       'radius_top_right':'0px',
#                       'radius_top_left':'0px'})
#context.box.hd.update({'background':'#ccc'})