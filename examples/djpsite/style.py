from djpcms.style import *


cssv.body.radius = px(4)

cssv.header.min_height = px(70)

cssv.footer.min_height = px(300)
cssv.footer.color = cssv.color.grayLighter 
cssv.footer.background = ('v','#222','#444')


css('#page-header',
    margin_top=cssv.topbar.height,
    padding_top=px(20))

css('.topbar',
    css('a.brand',
        height=cssv.topbar.height,
        padding=spacing(0,px(20))))