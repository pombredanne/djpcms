from djpcms.conf import settings
from djpcms.forms import model_to_dict
from djpcms.views.cache import pagecache
from djpcms.views import appsite
from djpcms.models import Page
from djpcms.forms.cms import PageForm

from django import test
from django.contrib.auth.models import User
from django.core.urlresolvers import clear_url_caches



class DjpCmsTestHandle(test.TestCase):
    '''Implements shortcut functions for testing djpcms.
Must be used as a base class for TestCase classes'''
    
    pagecache = pagecache
    Page = Page
    site = appsite.site
    
    def _pre_setup(self):
        super(DjpCmsTestHandle,self)._pre_setup()
        self.pagecache.clear()
        
    def _urlconf_setup(self):
        appurls = getattr(self,'appurls',None)
        if appurls:
            self._old_appurl = settings.APPLICATION_URL_MODULE
            settings.APPLICATION_URL_MODULE = appurls
        clear_url_caches()
            
    def _urlconf_teardown(self):
        if hasattr(self,'_old_appurl'):
            settings.APPLICATION_URL_MODULE = self._old_appurl
        appsite.site.clear()
        super(DjpCmsTestHandle,self)._urlconf_teardown()
    
    def clear(self, db = False):
        if db:
            self.Page.objects.all().delete()
        else:
            self.pagecache.clear()

    def makepage(self, view = None, model = None, bit = '', parent = None, fail = False, **kwargs):
        form = PageForm()
        data = model_to_dict(form.instance, form._meta.fields, form._meta.exclude)
        data.update(**kwargs)
        data.update({'url_pattern': bit,
                     'parent': None if not parent else parent.id})
        if view:
            if model:
                appmodel = self.site.for_model(model)
                view = appmodel.getview(view)
            else:
                view = self.site.getapp(view)
            data['application_view'] = view.code
        form = PageForm(data = data)
        if fail:
            self.assertFalse(form.is_valid())
        else:
            self.assertTrue(form.is_valid())
            instance = form.save()
            self.assertTrue(instance.pk)
            return instance

    def post(self, url = '/', data = {}, status = 200):
        '''Quick function for posting some content'''
        response = self.client.post(url,data)
        self.assertEqual(response.status_code,status)
        return response.context
    
    def get(self, url = '/', status = 200, response = False):
        '''Quick function for getting some content'''
        resp = self.client.get(url)
        self.assertEqual(resp.status_code,status)
        if response:
            return resp
        else:
            return resp.context
    
    def post(self, url = '/', data = {}, status = 200, response = False):
        '''Quick function for posting some content'''
        resp = self.client.post(url,data)
        self.assertEqual(resp.status_code,status)
        if response:
            return resp
        else:
            return resp.context
        
        
class TestCase(DjpCmsTestHandle):
        
    def setUp(self):
        p = self.get()['page']
        self.superuser = User.objects.create_superuser('testuser', 'test@testuser.com', 'testuser')
        self.user = User.objects.create_user('simpleuser', 'simple@testuser.com', 'simpleuser')
        self.assertEqual(p.url,'/')
        if not hasattr(self,'fixtures'):
            self.assertEqual(Page.objects.all().count(),1)
        
    def login(self, username = None, password = None):
        if not username:
            return self.client.login(username = 'testuser', password = 'testuser')
        else:
            return self.client.login(username = username,password = password)
        