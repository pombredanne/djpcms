'''Icons by Font-Awesome

https://github.com/FortAwesome/Font-Awesome'''
import os
from djpcms.media.style import *

css('@font-face',
    fontface('fontawesome/fontawesome-webfont', 'FontAwesome'),
    font_family="'FontAwesome'",       
    font_weight='normal',
    font_style='normal'
)

css('body',
    css_include(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'media','font-awesome.css')))

css('body',
    css_include(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'media','extra.css')))
