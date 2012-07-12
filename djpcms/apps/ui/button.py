from .base import *

cssv.button.margin = px(5)
cssv.button.font_weight = 'normal'
cssv.button.font_size = 'inherit'
cssv.button.font_family = 'inherit'
cssv.button.padding = spacing(cssv.input.padding.top, px(9), cssv.input.padding.bottom)
cssv.button.large.font_size = pc(120);
cssv.button.large.font_weight = 'bold'

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


selector = '.{0}'
css(selector.format(classes.button),
    padding=cssv.button.padding,
    display='inline-block',
    text_align='center',
    vertical_align='middle',
    font_weight=cssv.button.font_weight,
    font_size=cssv.button.font_size,
    font_family=cssv.button.font_family)

css(selector.format(classes.button+'.'+classes.button_small),
    radius(px(2)),
    font_weight='normal',
    padding=lazy(lambda: 0.5*cssv.button.padding))

css(selector.format(classes.button+'.'+classes.button_large),
    radius(cssv.input.radius),
    padding=lazy(lambda: 2*cssv.button.padding),
    font_size=cssv.button.large.font_size,
    font_weight=cssv.button.large.font_weight)