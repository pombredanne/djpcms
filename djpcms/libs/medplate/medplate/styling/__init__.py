import os
from copy import deepcopy

from djpcms.utils.importer import import_module 

from .style import default_data_theme, CssTheme, jquery_style_mapping


__all__ = ['make_theme','jQueryTheme']



def jQueryTheme(theme_name,jquery_theme):
    '''Associate a theme name with a jquery theme name'''
    jquery_style_mapping[theme_name] = jquery_theme


def make_theme(theme_name, data, jquery_theme):
    '''Create a theme'''
    for name,values in default_data_theme:
        CssTheme(name, theme_name, data = deepcopy(values))
    for name,values in data:
        CssTheme(name, theme_name, data = deepcopy(values))
    jQueryTheme(theme_name,jquery_theme)


def make():
    #loop over all module in themes and create style
    for fname in os.listdir(os.path.join(os.path.split(\
                                os.path.abspath(__file__))[0],'themes')):
        if fname.startswith('__'):
            continue
        if fname.endswith('.py'):
            fname = fname.split('.')[0]
            mod = import_module('medplate.styling.themes.{0}'.format(fname))
            if hasattr(mod,'data'):
                jquery_theme = getattr(mod,'jquery_theme',fname)
                make_theme(fname,mod.data,jquery_theme)
              
make()  