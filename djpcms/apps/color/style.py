'''Color picker plugin'''
from djpcms.media.style import *
import os

THIS_PATH = os.path.dirname(os.path.abspath(__file__))

css('body',
    css_include(os.path.join(THIS_PATH, 'media', 'color',
                             'colorpicker', 'jquery.colorpicker.css'),
                location='color/colorpicker'))