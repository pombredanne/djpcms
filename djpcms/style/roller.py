from medplate import CssTheme

def make_theme(theme_name, data):
    '''Create a theme'''
    for name,values in data.items():
        CssTheme(name, theme_name, data = values)
