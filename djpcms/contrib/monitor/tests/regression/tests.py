from datetime import datetime

from py2py3 import zip

from djpcms import test
from djpcms.contrib.monitor import link_models, linked
from djpcms.contrib.monitor.managers import LinkedManager
from djpcms.apps.included.user import UserApplication
from djpcms.utils.populate import populate

from userprofile.models import UserProfile


__all__ = ['DjangoStdNetLinkTest',
           'TestRedisMonitor',
           'appurls']

def appurls():
    return (
            UserApplication('/accounts/',UserProfile),
            )


names = populate('string',100,min_length=6,max_length=12)
passw = populate('string',100,min_length=6,max_length=12)


class DjangoStdNetLinkTest(test.TestCase):
    appurls = 'djpcms.contrib.monitor.tests.regression.appurls'
        
    def setUp(self):
        # you need to import django User here!
        from django.contrib.auth.models import User
        self.DjangoUser = User
        self.makesite()
        self.sites.load()
        link_models(User,UserProfile,
                    field_map = ['username',
                                 'password',
                                 'is_active'])
    
    def testLinked(self):
        self.assertEqual(UserProfile._meta.linked,self.DjangoUser)
        self.assertTrue(isinstance(UserProfile.objects,LinkedManager))
        all = list(linked(self.sites.settings.INSTALLED_APPS))
        self.assertEqual(len(all),1)
        self.assertEqual(all[0],UserProfile)
        
    def testCreate(self):
        u = self.DjangoUser(username = 'pinco', password = 'pallino')
        u.save()
        c = UserProfile.objects.get(id = u.id)
        self.assertEqual(c.djobject,u)
        return u
        
    def _testDerivedManager(self):
        self.assertFalse(isinstance(Environment.objects,LinkedManager))
        
    def testDelete(self):
        self.testCreate()
        self.assertTrue(UserProfile.objects.all().count())
        self.DjangoUser.objects.all().delete()
        self.assertFalse(UserProfile.objects.all().count())
        
    def testGet(self):
        username = self.testCreate().username
        user = self.DjangoUser.objects.get(username = username)
        profile = user.userprofile_linked
        self.assertEqual(profile.djobject,user)
        # now delete profile
        profile.delete()
        # still there
        profile = user.userprofile_linked
        self.assertRaises(UserProfile.DoesNotExist,
                          UserProfile.objects.get,
                          id = profile.id)
        user = self.DjangoUser.objects.get(username = username)
        # the linked object is recreated
        profile = user.userprofile_linked
        self.assertEqual(profile.djobject,user)
        
    def testUpdates(self):
        for nma,psw in zip(names,passw):
            try:
                self.DjangoUser(username = nma, password = psw).save()
            except:
                continue
        self.assertEqual(self.DjangoUser.objects.all().count(),
                         UserProfile.objects.all().count())
            

class TestRedisMonitor(test.TestCase,test.UserMixin):
    
    def setUp(self):
        self.makesite()
        self.makesite('/admin/',appurls = self.sites.make_admin_urls)
        self.sites.load()
        self.makeusers()
        self.login()
        
    #def testAddServer(self):
    #    response = self.get('/admin/monitor/redis/add/')
    #    html = response.content