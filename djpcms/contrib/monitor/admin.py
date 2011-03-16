
from .applications import RedisMonitorApplication
from .models import RedisServer


admin_urls = (
              RedisMonitorApplication('/redis/',
                                      RedisServer,
                                      name = 'Redis monitor',
                                      list_display = ['host','port','notes']),
        )
              