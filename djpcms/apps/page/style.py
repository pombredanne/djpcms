'''Uniform Styling
'''
from djpcms.media.style import *

################################################################################
##    VARIABLES
cssv.header.background = None
cssv.header.color = None
cssv.header.min_height = None
cssv.header.margin = None
cssv.header.position = None
cssv.header.top = None

cssv.content.background = None
cssv.content.color = None
cssv.content.min_height = None
cssv.content.position = 'relative'
cssv.content.top = None
cssv.content.bottom = None
#
cssv.footer.min_height = None
cssv.footer.background = None
cssv.footer.color = None
cssv.footer.font_size = None

################################################################################

css('#page-header',
    bcd(**cssv.header.params()),
    width=pc(100),
    min_height=cssv.header.min_height,
    position=cssv.header.position,
    top=cssv.header.top)

css('#page-content',
    bcd(**cssv.content.params()),
    width=pc(100),
    min_height=cssv.content.min_height,
    position=cssv.content.position,
    top=cssv.content.top,
    bottom=cssv.content.bottom)

css('#page-footer',
    bcd(**cssv.footer.params()),
    position='absolute',
    bottom=0,
    width=pc(100),
    min_height=cssv.footer.min_height,
    font_size=cssv.footer.font_size)