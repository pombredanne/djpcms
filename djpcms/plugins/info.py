

from djpcms.plugins import DJPplugin
from django.template import loader
from djpcms.utils import version


class PoweredBy(DJPplugin):
    name = 'poweredby'
    description = 'Powered by panel'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''
        Information about the packages used to power the web-site
        '''
        v = version.get()
        p = v.pop('python')
        d = v.pop('django')
        c = {'python': p.get('version'),
             'django': d.get('version'),
             'other':  v.values()}
        return loader.render_to_string(['/bits/powered_by.html',
                                        'djpcms/bits/powered_by.html'],
                                        c)
        
        
class Deploy(DJPplugin):
    name = 'deploysite'
    description = 'Deploy Timestamp'
    
    def render(self, djp, wrapper, prefix, **kwargs):
        '''
        Information about deployment
        '''
        from djpcms.models import DeploySite
        from djpcms.utils import cdt
        try:
            latest = DeploySite.objects.latest()
        except:
            return ''
        return loader.render_to_string(['/bits/deploy.html',
                                        'djpcms/bits/deploy.html'],
                                        {'latest':latest,
                                         'cdt': cdt.link()})