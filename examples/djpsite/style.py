from djpcms.media.style import *

cssv.header.min_height = px(70)
cssv.content.min_height = px(400)
cssv.footer.min_height = px(300)

with cssv.theme('smooth') as t:
    t.body.background = '#222'
    t.header.background = '#fafafa'
    t.content.background = ('v', '#fafafa', '#fff')
    t.footer.color = t.color.grayLighter
    t.footer.background = ('v','#444','#222')
    
    
with cssv.theme('green') as t:
    t.body.background = '#222'
    t.body.radius = px(4)
    
    t.header.background = '#94BA65'
    t.content.background = ('v', '#94BA65', '#fff')
    t.footer.color = t.color.grayLighter
    t.footer.background = ('v','#444','#222')
    
    t.clickable.default.background = ('v', 'A9BC7F', 'A9BC7F')
    t.clickable.default.color = '#000'
    t.clickable.hover.background = ('v', '8E9E6B', '8E9E6B')
    t.clickable.active.background = ('v', 'DEF7A7', 'DEF7A7')
    
    t.widget.head.background = ('v', 'D47333', 'D48957')


css('#page-header',
    text_align='center',
    padding=px(10),
    line_height=px(20))
#
css('.topbar',
    css('a.brand',
        height=cssv.topbar.height,
        padding=spacing(0,px(20))))