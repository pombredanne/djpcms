'''Make themes and add them to LOCATION

To use::

    python maketheme.py smooth
    
will create a css file at

LOCATION/smooth.css
'''
import os
import sys

import manage

APPLICATIONS = 'jquery_mtree djpkit bsmselect'
LOCATION = 'jquery_mtree/media/jquery_mtree/themes/'

if __name__ == '__main__':
    if len(sys.argv) == 2:
        style = sys.argv[1]
    else:
        style = 'smooth'
    
    command = 'python manage.py style ' + APPLICATIONS
    command += ' --style={0} --media=/media/ --target={1}{0}.css'.format(style,LOCATION)
    os.system(command)
    
