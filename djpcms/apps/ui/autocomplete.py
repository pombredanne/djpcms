from .base import *

css('.ui-autocomplete',
    css('li',
        css('a',
            clickable(default=bcd(
                    background='inherit',
                    color='inherit',
                    text_decoration='none',
                    border=border(color='transparent',
                                  style=cssv.clickable.default.border.style,
                                  width=cssv.clickable.default.border.width)),
                      hover=bcd(**cssv.clickable.hover.params()),
                      active=bcd(**cssv.clickable.active.params())),
            padding=cssv.input.padding,
            display='block'),
        padding=0,),
    padding=0,
    position='absolute',
    cursor='default')    

css('* html .ui-autocomplete', width=px(1))