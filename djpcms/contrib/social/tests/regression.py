from djpcms import test
from djpcms.contrib.social.defaults import User
from djpcms.contrib.social import OAuthProvider
from djpcms.contrib.social.applications import SocialUserApplication


appurls = SocialUserApplication('/accounts/', User),


class oauthtest(OAuthProvider):
    '''Test server from http://term.ie/oauth/example/'''
    REQUEST_TOKEN_URL = 'http://term.ie/oauth/example/request_token.php'
    ACCESS_TOKEN_URL  = 'http://term.ie/oauth/example/access_token.php'
    #AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'


class SocialTest(test.TestCase):
    appurls = 'djpcms.contrib.social.tests'
    
    def testRequest(self):
        resp = self.get('/accounts/oauthtest/login/', status = 302, response = True)