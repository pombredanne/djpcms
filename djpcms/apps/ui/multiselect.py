from .forms import *

cssv.bsm.background = cssv.color.grayLighter

css('.multiSelectContainer',
    cssb('.{0} + .{0}'.format(classes.ui_input),
         margin_top=em(0.25),
         overflow='hidden'),
    cssb('.{0}'.format(classes.ui_input),
         css('ul',
             cssb('li',
                  margin=0,
                  width=pc(100),
                  padding=spacing(cssv.input.padding.top, 0, cssv.input.padding.bottom)),
            margin=0,
            padding=0,
            width=pc(100),
            float='left')),
    css('.disabled',
        opacity(cssv.disabled.opacity)),
    overflow='hidden')

css('.multiSelectList',
    css('li',
        cssb('span',
             float='left'),
        cssb('a',
             float='right'),
        float='left',
        position='relative',
        list_style='none'),
    position='relative',
    display='block',
    list_style='none')