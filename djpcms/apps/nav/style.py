'''Top bar styling
'''
from djpcms.apps.nav import topbar_class, topbar_fixed

from pycss import css, fixtop
from pycss.elements.topbar import topbar

css('.'+topbar_class, topbar())
css('.'+topbar_fixed, fixtop())
