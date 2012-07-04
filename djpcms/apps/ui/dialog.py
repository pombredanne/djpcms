'''Style pop up dialog.'''
from djpcms.media.style import *


css('.%s' % classes.dialog,
    position='absolute',
    overflow='hidden',
    width=px(300))