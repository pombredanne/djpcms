'''\
A sophisticated dynamic application for managing page content
and page layout via the content block API.
To use this application you need to set the :setting:`CMS_ORM`
to either ``stdnet`` or ``django`` and register the application
with one site (usually an admin site).
'''
from .blocks import *
from .forms import *
from .layout import *