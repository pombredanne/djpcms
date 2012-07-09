from .base import *

cssv.button.margin = px(5)
cssv.button.font_weight = 'normal'
cssv.button.font_size = 'inherit'
cssv.button.padding = spacing(cssv.input.padding.top, px(9), cssv.input.padding.bottom)

css('.%s' % classes.button_group,
    clearfix(),
    cssb('.%s' % classes.button,
         cssa(':first-child', radius(radius_left), margin=0),
         cssa(':last-child', radius(radius_right)),
         radius(0),
         float='left',
         position='relative',
         margin=spacing(0, 0, 0, px(-1))),
    display='block')

css('.%s' % classes.button_holder,
    clearfix(),
    cssb('*',
         cssa(':last-child', margin=0),
         margin=spacing(0,cssv.button.margin.right,0,0)))


selector = 'input.{0}[type="submit"], button.{0}, a.{0}, label.{0}'
css(selector.format(classes.button),
    padding=cssv.button.padding,
    display='inline-block',
    text_align='center',
    vertical_align='middle',
    font_weight=cssv.button.font_weight,
    font_size=cssv.button.font_size)

css(selector.format(classes.button+'.'+classes.button_small),
    radius(px(2)),
    padding=px(2))

css(selector.format(classes.button+'.'+classes.button_large),
    radius(cssv.input.radius),
    padding=2*cssv.input.padding)