from djpcms.apps.admin import AdminApplicationSimple
                                        
from .applications import *
from .models import RedisServer, Log

from stdnet.orm.base import Metaclass


admin_urls = (
              RedisMonitorApplication('/redis/',
                                       RedisServer,
                                       name = 'Redis monitor'),
              StdModelApplication('/stdnet/',
                                  Metaclass,
                                  name = 'StdNet Models'),
              AdminApplicationSimple('/logs/',
                    Log,
                    name='logs',
                    list_display = ('timestamp','level','source',
                                    'msg','host','user'),
                    object_display = ('timestamp','level','source',
                                      'host','msg')
            )
)

