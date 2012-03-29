'''Uniform Styling
'''
from djpcms.style import *

################################################################################
##    VARIABLES
cssv.footer.min_height = None
cssv.footer.background = None
cssv.footer.color = None

################################################################################

css('#page-footer',
    gradient(cssv.footer.background),
    color = cssv.footer.color,
    min_height = cssv.footer.min_height)