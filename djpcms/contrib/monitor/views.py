from datetime import datetime, timedelta
from distutils.version import StrictVersion

from py2py3 import iteritems, ispy3k

if ispy3k:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

from stdnet.lib.redisinfo import RedisStats

import djpcms
from djpcms import forms
from djpcms.html import Paginator, table_checkbox, icons, Table
from djpcms.utils.ajax import jhtmls, jredirect
from djpcms.utils import lazyattr, gen_unique_id
from djpcms.template import loader
from djpcms.views import *

from stdnet.orm import model_iterator

