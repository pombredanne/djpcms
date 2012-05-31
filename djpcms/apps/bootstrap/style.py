'''Uniform Styling
'''
from djpcms.style import *

cssv.popover.zindex = 1000


css('.popover',
    cssa('.top', margin_top = '-5px'),
    cssa('.right', margin_left = '5px'),
    cssa('.bottom', margin_top = '5px'),
    cssa('.left', margin_left = '-5px'),
    position = 'absolute',
    top = 0,
    left = 0,
    z_index = cssv.popover.zindex,
    padding = '5px',
    display = 'none'
)

