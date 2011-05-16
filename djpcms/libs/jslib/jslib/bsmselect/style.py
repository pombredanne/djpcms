from medplate import CssContext, CssTheme


mtree = CssContext('bsmselect',
                   tag = '.bsmSelect',
                   template = 'bsmselect/bsmselect.css_t',
                   data = {
                           'display': 'inline'
                           #'hovered_background': '#e7f4f9',
                           #'hovered_border':'1px solid #e7f4f9'
                           #
                           #'clicked_background': 'navy',
                           #'clicked_color':'white'
                           }
                   )