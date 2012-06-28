'''An application for managing page content
and page layout via the content block API.

To use this application you need to have installed a CMS application
which implements the :mod:`djpcms.core.page` interface and include
``djpcms.apps.contentedit`` in your ``INSTALLED_APPS`` list.
'''
from .sitemap import *
from .blocks import *
from .forms import *
from .layout import *