from .applications import *
from .models import Server

from stdnet.orm.base import Metaclass

admin_urls = (
              RedisMonitorApplication('/redis/',
                                       RedisServer,
                                       name = 'Redis monitor',
                                       list_display = ['host','port','notes']),
              StdModelApplication('/stdnet/',
                                  Metaclass,
                                  name = 'StdNet Models')
        )

