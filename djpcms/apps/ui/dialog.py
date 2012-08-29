'''Style pop up dialog.'''
from .base import *

cssv.dialog.border.color = cssv.color.grayLighter
cssv.dialog.border.width = cssv.widget.border.width
cssv.dialog.border.style = cssv.widget.border.style
cssv.dialog.head.background = '#ededed'
cssv.dialog.head.color = '#333'
cssv.dialog.shadow = '0 0 5px 5px #888'
cssv.dialog.head.font_weight = 'bold'
cssv.dialog.head.font_size = pc(110)


css('.%s' % classes.dialog,
    radius(cssv.widget.radius),
    border(**cssv.dialog.border.params()),
    shadow(cssv.dialog.shadow),
    css('.ui-dialog-titlebar',
        radius(radius_top),
        bcd(**cssv.dialog.head.params()),
        border(color=cssv.dialog.border.color,
               style=cssv.dialog.border.style,
               width=spacing(0, 0, cssv.dialog.border.width.bottom, 0)),
        font_weight=cssv.dialog.head.font_weight,
        font_size=cssv.dialog.head.font_size),
    css('.ui-dialog-content', border='none'),
    css('.ui-dialog-buttonpane',
        bcd(**cssv.dialog.head.params()),
        radius(radius_bottom),
        border(color=cssv.dialog.border.color,
               style=cssv.dialog.border.style,
               width=spacing(cssv.dialog.border.width.bottom, 0, 0, 0))),
    css('.ui-dialog-buttonset',
        float='right'),
    position='absolute',
    overflow='hidden',
    padding=0,
    width=px(300),
    comment='Pop up dialog')