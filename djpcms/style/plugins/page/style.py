'''Uniform Styling
'''
from djpcms.style import *

################################################################################
##    VARIABLES
cssv.header.background = None
cssv.header.min_height = None

cssv.content.color = None
cssv.content.min_height = None
cssv.content.background = None
cssv.content.color = None
#
cssv.footer.min_height = None
cssv.footer.background = None
cssv.footer.color = None

################################################################################

css('#page-header',
    gradient(cssv.header.background),
    color=cssv.header.color,
    min_height=cssv.header.min_height)

css('#page-content',
    gradient(cssv.content.background),
    color = cssv.content.color,
    min_height = cssv.content.min_height)

css('#page-footer',
    gradient(cssv.footer.background),
    color = cssv.footer.color,
    min_height = cssv.footer.min_height)