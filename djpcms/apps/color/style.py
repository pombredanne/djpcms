'''Color picker plugin'''
from djpcms.media.style import *

cssv.color_picker.background = cssv.color.grayLighter

css('.color-picker',
    cssa('.wheel',
         background=cssv.color_picker.background,
         position='absolute'))