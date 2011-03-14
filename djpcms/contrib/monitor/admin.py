
from .applications import StdnetMonitorApplication


admin_urls = (
              StdnetMonitorApplication('/redis/',
                                       name = 'Redis monitor'),
        )
              