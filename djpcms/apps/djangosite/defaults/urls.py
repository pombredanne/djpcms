from django.conf.urls.defaults import *
from djpcms import sites

urlpatterns = patterns('', *sites.all())