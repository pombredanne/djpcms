#
# I assume djpcms is on the same workspace
#
# To create a style for djpcms do this
#
# python manage.py style -s smooth -m /media/ -t jquery_mtree/media/jquery_mtree/themes/smooth.css
#
#
import os
import sys
try:
    import djpcms
except:
    p = lambda x : os.path.split(x)[0]
    path = os.path.join(p(p(p(os.path.abspath(__file__)))),'djpcms')
    sys.path.insert(0,path)
    import djpcms

from djpcms.apps.management import execute

djpcms.MakeSite(__file__,
                CMS_ORM = 'django',
                MEDIA_URL = '../../djpcms/djpcms/media/',
                TEMPLATE_ENGINE = 'django',
                INSTALLED_APPS= ('djpcms',
                                 'medplate',
                                 'djpkit',
                                 'bsmselect',
                                 'jquery_mtree'))

if __name__ == '__main__':
    execute()