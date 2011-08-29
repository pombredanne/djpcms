'''djpcms settings for testing.
'''
import os
INSTALLED_APPS  = ['djpcms',
                   'fileupload']
INCLUDE_TEST_APPS = ['regression.djptest']
CUR_DIR = os.path.split(os.path.abspath(__file__))[0]
SITE_ID = 1
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3'}}
MEDIA_ROOT = os.path.join(CUR_DIR, 'media')
TEMPLATE_DIRS = os.path.join(CUR_DIR, 'templates'),
SOCIAL_OAUTH_CONSUMERS = {'oauthtest':('key','secret')}
#extensions = ['djpcms.contrib.flowrepo.markups.rst.ext.pngmath']
extensions = ['sphinx.ext.pngmath']
