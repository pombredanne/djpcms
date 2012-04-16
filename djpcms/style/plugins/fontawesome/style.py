import os
from djpcms.style import *

css('@font-face',
    fontface('fontawesome/fontawesome-webfont', 'FontAwesomeRegular'),
    font_family="'FontAwesome'",       
    font_weight='normal',
    font_style='normal'
)

css('body',
    css_include(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'media','font-awesome.css')))