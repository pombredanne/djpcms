'''Uniform Styling
'''
from medplate import CssContext, CssTheme, variables, gradient, radius, shadow


CssContext('popover',
           tag = '.popover',
           template = 'medplate/popover.css_t',
           data = {'position': 'absolute',
                   'top': '0,',
                   'left': '0',
                   'z-index': 1000,
                   'padding': '5px',
                   'display': 'none'}
)

