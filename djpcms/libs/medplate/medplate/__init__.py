from .css import CssContext, CssTheme, CssBody, rendercss


#________________________________________ ANCHOR
CssContext('anchor',
           tag = 'a',
           template = 'medplate/anchor.css_t',
           data = {
                   'text_decoration': 'none',
                   'weight':'normal',
                   'color':'#33789C',
                   'background': 'transparent',
                   'color_hover':'#204C64',
                   'background_hover':None
                   }
           )