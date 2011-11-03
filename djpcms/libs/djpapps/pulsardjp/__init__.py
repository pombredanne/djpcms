'''\
A pulsar application for serving djpcms_ powered web sites.
It includes a :class:`pulsar.apps.tasks.Task` implementation
with Redis backend which uses stdnet_.

To use it:

* Add ``pulsar.apps.pulsardjp`` to the list of ``INSTALLED_APPS``.
* type::

    python manage.py run_pulsar


.. _djpcms: https://github.com/lsbardel/djpcms
.. _stdnet: http://lsbardel.github.com/python-stdnet/
'''
import os

import djpcms

from pulsar.apps import wsgi

from .models import *
from .forms import *


def set_proxy_function(sites, proxy):
    for site in sites:
        for app in site.applications:
            if hasattr(app,'proxy') and app.proxy == None:
                app.proxy = proxy
                

class SiteLoader(djpcms.SiteLoader):
    settings = None
    ENVIRON_NAME = 'PULSAR_SERVER_TYPE'
    
    
class WSGIApplication(wsgi.WSGIApplication):
    
    def handler(self):
        loader = self.callable
        middleware = loader.wsgi_middleware()
        resp = loader.response_middleware()
        return self.wsgi_handler(middleware,resp)
        