from djpcms.media.style import *

cssv.definition_list.spacing = px(3)
cssv.definition_list.opacity = 0.8
cssv.definition_list.font_weight = 'normal'

################################################# OBJECT DEFINITIONS
css('.%s' % classes.object_definition,
    css('dl',
        cssa(':first-child', margin_top=0),
        css('dt',
            opacity(cssv.definition_list.opacity),
            font_weight=cssv.definition_list.font_weight,
            float='left',
            width='40%',
            margin=0),
        css('dd', margin = 0),
        cssa('.w20 dt', width='20%'),
        cssa('.w40 dt', width='40%'),
        cssa('.w50 dt', width='50%'),
        float='left',
        width=pc(100),
        margin= spacing(cssv.definition_list.spacing, 0, 0)),
    float='left')