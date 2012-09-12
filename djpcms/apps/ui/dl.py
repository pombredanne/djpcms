from djpcms.media.style import *

cssv.definition_list.spacing = px(3)
cssv.definition_list.opacity = 0.8
cssv.definition_list.font_weight = 'normal'

################################################# OBJECT DEFINITIONS
class dl(mixin):
    
    def __init__(self, width):
        self.width = pc(width)
        
    def __call__(self, elem):
        css('dl',
            css('dt', width=self.width),
            css('dd', margin_left=self.width),
            parent=elem)
        
        
css('.%s' % classes.object_definition,
    css('dl',
        cssa(':first-child', margin_top=0),
        css('dt',
            opacity(cssv.definition_list.opacity),
            font_weight=cssv.definition_list.font_weight,
            float='left',
            margin=0),
        css('dd', margin=0),
        float='left',
        width=pc(100),
        margin= spacing(cssv.definition_list.spacing, 0, 0)),
    float='left',
    width=pc(100),
    comment='Object definition list')


css('.%s' % classes.object_definition,
    dl(40),
    cssa('.w20', dl(20)),
    cssa('.w30', dl(30)),
    cssa('.w50', dl(50)))