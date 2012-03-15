import sys
import os
import json
ispy3k = sys.version[0] == '3'

if ispy3k:
    from urllib.request import Request, build_opener, install_opener
    from urllib.request import ProxyHandler, URLError
    from urllib.parse import urlencode
else:
    from urllib2 import Request, build_opener, install_opener
    from urllib2 import ProxyHandler, URLError
    from urllib import urlencode
 
# http://www.geonames.org/export/geonames-search.html


class Response(object):
    
    def __init__(self, response):
        self.response = response
        
    @property
    def status(self):
        return self.response.code
    
    @property
    def reason(self):
        return self.response.reason
    
    @property
    def content(self):
        if not hasattr(self,'_content'):
            self._content = self.response.read()
        return self._content
    
    def content_string(self):
        return self.content.decode()


class HttpClient(object):
    DEFAULT_HEADERS = {'user-agent': 'Python-geonames'}
    
    def headers(self, headers):
        d = self.DEFAULT_HEADERS.copy()
        if not headers:
            return d
        else:
            d.update(headers)
        return d
    
    def __init__(self, proxy_info = None, timeout = None,
                 headers = None):
        handlers = [ProxyHandler(proxy_info)]
        self._opener = build_opener(*handlers)
        self.timeout = timeout
        
    def request(self, url, body=None, **kwargs):
        if body and not isinstance(body,bytes):
            body = body.encode('utf-8')
        response = self._opener.open(url,data=body,timeout=self.timeout)
        return Response(response)
 

class Geonames(object):
    PROXY_INFO = None
    search_url = 'http://ws.geonames.org/searchJSON?'
    
    def __init__(self, httpclient = None):
        self.httpclient = httpclient or\
                          HttpClient(proxy_info = self.PROXY_INFO)
        
    def search(self, q, maxRows = 10):
        http = self.httpclient
        body = urlencode({'q': q,'maxRows': maxRows,
                          'lang': 'en',
                          'style': 'full'})
        response = http.request(self.search_url,body)
        if response.status == 200:
            data = json.loads(response.content.decode('utf-8'))
            if not data['geonames']:
                return None
            return data['geonames'][:maxRows]
 


if __name__ == '__main__':
    g = Geonames()
    r = g.search('london')
    print(r)