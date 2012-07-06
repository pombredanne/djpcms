from .base import *

cssv.button.padding = spacing(cssv.input.padding.top, px(9), cssv.input.padding.bottom)

css('.%s' % classes.button_group,
    clearfix(),
    cssb('button',
         cssa(':first-child', radius(radius_left), margin=0),
         cssa(':last-child', radius(radius_right)),
         radius(0),
         float='left',
         position='relative',
         margin=spacing(0, 0, 0, px(-1))),
    display='block')


css('input.{0}[type="submit"], button, a.{0}'.format(classes.button),
    padding=cssv.button.padding,
    display='inline-block')

css('button.{1},a.{0}.{1},input.{0}.{1}[type="submit"]'\
        .format(classes.button, classes.button_small),
    radius(px(2)),
    padding=px(2))

css('button.{0},a.button.{0},input.button.{0}[type="submit"]'\
        .format(classes.button_large),
    radius(cssv.input.radius),
    padding=2*cssv.input.padding)