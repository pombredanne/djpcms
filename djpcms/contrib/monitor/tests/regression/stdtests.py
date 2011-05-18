from djpcms import test
from djpcms.contrib.monitor import installed_models


class TestMonitor(test.TestCase):
    
    def setUp(self):
        self.makesite()
        
    def testInstalledModels(self):
        models = list(installed_models(self.sites,['djpcms']))
        self.assertEqual(len(models),5)
        models = list(installed_models(self.sites,['djpcms.page']))
        self.assertEqual(len(models),1)
        self.assertEqual(str(models[0]._meta),'djpcms.page')
        models = list(installed_models(self.sites,['djpcms','sessions']))
        self.assertEqual(len(models),12)