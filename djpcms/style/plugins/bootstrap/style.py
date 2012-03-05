'''Uniform Styling
'''
from djpcms.style import css, cssc, cssv

cssv.declare('popover_zindex',1000)


css('.popover',
    cssc('.top', margin_top = '-5px'),
    cssc('.right', margin_left = '5px'),
    cssc('.bottom', margin_top = '5px'),
    cssc('.left', margin_left = '-5px'),
    position = 'absolute',
    top = 0,
    left = 0,
    z_index = cssv.popover_zindex,
    padding = '5px',
    display = 'none'
)

