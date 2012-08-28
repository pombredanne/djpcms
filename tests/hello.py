from djpcms.utils import test


class TestHelloWorld(test.TestCase):
    
    def website(self):
        from helloworld import HelloWorld
        return HelloWorld()
        
    def testSite(self):
        site = self.site()
        self.assertEqual(len(site), 1)
        
    def testGet(self):
        client = self.client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)
        text = response.content_string()
        self.assertTrue('Hello World!' in text)
        self.assertEqual(response.headers['content-type'], 'text/html')
        self.assertEqual(len(response.content),
                         int(response.headers['content-length']))