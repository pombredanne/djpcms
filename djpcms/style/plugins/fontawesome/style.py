import os
from djpcms.style import *


class fontface(mixin):
    
    def __init__(self, base):
        self.base = base
        
    def __call__(self, elem):
        base = self.base
        if not base.startswith('http'):
            base = cssv.MEDIAURL.value + self.base
        elem['src'] = "url('{0}.eot')".format(base)
        elem['src'] = "url('{0}.eot?#iefix') format=('embedded-opentype'), "\
                      "url('{0}.woff') format('woff'), "\
                      "url('{0}.ttf') format('truetype'), "\
                      "url('{0}.svgz#FontAwesomeRegular') format('svg'), "\
                      "url('{0}.svg#FontAwesomeRegular') format('svg')"\
                      .format(base)

css('@font-face',
    fontface('fontawesome/font/fontawesome-webfont'),
    font_family='"FontAwesome"',       
    font_weight='normal',
    font_style='normal'
)

css_include(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'media','fontawesome','font-awesome.css'))