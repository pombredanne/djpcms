import time
from datetime import datetime, timedelta

from djpcms.utils import test
from djpcms.core.http.wrappers import RequestNode, Request, BytesIO


class Http(test.TestCase):
    
    def makeRequest(self, **kwargs):
        environ = self.environ(**kwargs)
        path = environ['PATH_INFO']
        environ['DJPCMS'] = RequestNode(None,None,path)
        return Request(environ,None,None,path)
    
    def environ(self, method = 'POST', input = b'', path = None):
        return {'PATH_INFO': path or '/',
                'REQUEST_METHOD': method,
                'CONTENT_LENGTH':len(input),
                'wsgi.input': BytesIO(input)}
        
    def testRequest(self):
        request = self.makeRequest(path = 'bodus', method = 'bogus')
        self.assertFalse(request.GET)
        self.assertFalse(request.POST)
        self.assertFalse(request.COOKIES)
        self.assertTrue(request.environ)
        self.assertEqual(request.environ['PATH_INFO'], 'bogus')
        self.assertEqual(request.environ['REQUEST_METHOD'], 'bogus')

    def test_parse_cookie(self):
        self.assertEqual(http.parse_cookie('invalid:key=true'), {})

    def test_httprequest_location(self):
        request = self.makeRequest()
        self.assertEqual(\
            request.build_absolute_uri(location="https://www.example.com/asdf"),
            'https://www.example.com/asdf')

        #request.get_host = lambda: 'www.example.com'
        #request.path = ''
        #self.assertEqual(request.build_absolute_uri(location="/path/with:colons"),
        #    'http://www.example.com/path/with:colons')

    def test_near_expiration(self):
        "Cookie will expire when an near expiration time is provided"
        response = http.Response(self.environ())
        # There is a timing weakness in this test; The
        # expected result for max-age requires that there be
        # a very slight difference between the evaluated expiration
        # time, and the time evaluated in set_cookie(). If this
        # difference doesn't exist, the cookie time will be
        # 1 second larger. To avoid the problem, put in a quick sleep,
        # which guarantees that there will be a time difference.
        expires = datetime.utcnow() + timedelta(seconds=10)
        time.sleep(0.1)
        response.set_cookie('datetime', expires=expires)
        datetime_cookie = response.cookies['datetime']
        self.assertEqual(datetime_cookie['max-age'], 10)

    def test_far_expiration(self):
        "Cookie will expire when an distant expiration time is provided"
        response = http.Response(self.environ())
        response.set_cookie('datetime', expires=datetime(2028, 1, 1, 4, 5, 6))
        datetime_cookie = response.cookies['datetime']
        self.assertEqual(datetime_cookie['expires'], 'Sat, 01-Jan-2028 04:05:06 GMT')

    def test_max_age_expiration(self):
        "Cookie will expire if max_age is provided"
        response = http.Response(self.environ())
        response.set_cookie('max_age', max_age=10)
        max_age_cookie = response.cookies['max_age']
        self.assertEqual(max_age_cookie['max-age'], 10)
        self.assertEqual(max_age_cookie['expires'], http.cookie_date(time.time()+10))

    def test_httponly_cookie(self):
        response = http.Response(self.environ())
        response.set_cookie('example', httponly=True)
        example_cookie = response.cookies['example']
        # A compat cookie may be in use -- check that it has worked
        # both as an output string, and using the cookie attributes
        self.assertTrue('; httponly' in str(example_cookie))
        self.assertTrue(example_cookie['httponly'])

    def test_stream(self):
        request = self.makeRequest(input = b'name=value')
        self.assertFalse('raw_post_data' in request.cache)
        self.assertEqual(request.POST, {'name': ['value']})
        self.assertEqual(request.cache['raw_post_data'], b'name=value')

