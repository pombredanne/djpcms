from .applications import *
from .models import RedisServer

from stdnet.orm.base import Metaclass


admin_urls = (
              RedisMonitorApplication('/redis/',
                                       RedisServer,
                                       name = 'Redis monitor'),
              StdModelApplication('/stdnet/',
                                  Metaclass,
                                  name = 'StdNet Models')
              )

