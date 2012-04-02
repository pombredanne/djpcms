'''Style inputs, widgets and forms used by djpcms 
'''
from djpcms.style import *

################################################################################
##    VARIABLES
cssv.widget.hd.font_size = cssv.body.font_size
cssv.widget.hd.font_weight = 'normal'
cssv.widget.padding = spacing(px(5))
cssv.widget.hd.padding = cssv.widget.padding
cssv.widget.bd.padding = cssv.widget.padding
cssv.widget.ft.padding = cssv.widget.padding
#
cssv.disabled.opacity = 0.7
cssv.disabled.cursor = 'not-allowed'
#
cssv.input.vertical_padding = px(4)
cssv.input.border_width = px(1)
cssv.input.border_color = cssv.color.grayLight
cssv.input.radius = px(0)
cssv.input.padding = cssv.input.vertical_padding
cssv.input.focus_color = None
cssv.input.focus_shadow = '0 3px 3px rgba(0,0,0,0.2)'
cssv.input.required_font_weight = 'None'
#
cssv.button.padding = spacing(cssv.input.vertical_padding, 9)
cssv.button.default.background = ('v',cssv.color.white,cssv.color.grayLighter)
cssv.button.hover.background = cssv.color.grayLighter
cssv.button.active.background = ('v',cssv.color.grayLighter,
                                 cssv.color.grayLight)
cssv.button.border_color = cssv.color.grayLight
#
cssv.uniform.padding = px(4)
cssv.uniform.table_layout = 'auto'
################################################################################


################################################# CLEARINPUT
class clearinp(mixin):
    '''For clearing floats to all *elements*.'''    
    def __call__(self, elem):
        elem['border'] = 'none'
        elem['outline'] = 'none'


################################################# DJPCMS BOX
css('.djpcms-html-box',
    css('.collapsed > .bd', display = 'none'))

################################################# WIDGET
css('.widget',
    css('.hd',
        css('h1,h2,h3,h4,h5',
            font_size = cssv.widget.hd.font_size,
            font_weight = cssv.widget.hd.font_weight,
            float = 'left',
            padding = 0,
            margin = 0,
            background = 'transparent'
        ),
        padding = cssv.widget.hd.padding,
        overflow='hidden',
    ),
    css('.bd',
        padding = cssv.widget.bd.padding,
        overflow = 'hidden',
        border = 'none'),
    css('.ft',
        padding = cssv.widget.ft.padding,
        overflow = 'hidden',
        border = 'none')
)

################################################# OBJECT DEFINITIONS
css('.object-definition',
    css('dl',
        cssa(':first-child', margin_top = 0),
        css('dt',
            opacity = cssv.definition_list_opacity,
            float = 'left', width = '40%', margin = 0),
        css('dd', margin = 0)
        ),
    cssa('.w20 dl dt', width = '20%'),
    cssa('.w40 dl dt', width = '40%'),
    cssa('.w50 dl dt', width = '50%'),
    overflow = 'hidden',
    margin = '5px 0 0')

################################################################################
# Uniform variables
################################################################################



disabled_selector = '''\
.disabled .field-widget, .readonly .field-widget, 
input[disabled], select[disabled], textarea[disabled],
input[readonly], select[readonly], textarea[readonly]
''' 

def size(n):
    if n == 1:
        return 30
    else:
        return 60*(n-1)
    
    
def process_elems(elem, data):
    '''Consistent padding using the ``uniform_padding`` variable'''
    p = cssv.uniform_padding.value
    if elem.name == 'uniformtable-elems':
        data.update({'padding': '{0}px 0 {0}px {0}px'.format(p)})
    elif elem.name == 'uniformtable-errors':
        data.update({'padding': '0 0 0 {0}px'.format(p)})
    elif elem.name == 'uniform-errorlist':
        data.update({'margin': '{0}px 0 0'.format(p),
                     'padding': p})
    return data

        
        
################################################################################
#    INPUT FIELDS
################################################################################
css('.field-widget',
    css('input[type="text"],input[type="password"],textarea,select',
        clearinp(),
        line_height = 1,
        padding = 0,
        margin = 0,
        width = '100%',
        background = 'transaprent'),
    css('input:focus,textarea:focus,select:focus', clearinp()),
    radius(cssv.input.radius),
    padding = cssv.input.padding,
    border_style='solid',
    border_width=cssv.input.border_width,
    border_color=cssv.input.border_color)

css('.field-widget.focus',
    shadow(cssv.input.focus_shadow),
    border_color = cssv.input.focus_color)

for n in range(1,10):
    css('.field-widget.span{0}'.format(n),
         width = '{0}px'.format(size(n)))

################################################################################
#    BUTTONS
################################################################################
#'button.button,a.button,input.button[type="submit"]'
css('input.button[type="submit"]',
    clickable(bcd(**cssv.button.default.params()),
              bcd(**cssv.button.hover.params()),
              bcd(**cssv.button.active.params())),
    radius(cssv.input.radius),
    padding = cssv.button.padding,
    color=cssv.button.color,
    border_style='solid',
    border_width=cssv.input.border_width,
    border_color=cssv.button.border_color,
    cursor='pointer',
    display='inline-block',
    margin_right=px(4))

css('button.button.large,a.button.large,input.button.large[type="submit"]',
    radius(cssv.input.radius),
    padding = 2*cssv.input.padding)

css('.required label',
    font_weight = cssv.input_required_font_weight)

css(disabled_selector,
    opacity(cssv.disabled.opacity),
    cursor =  cssv.disabled.cursor)


################################################################################
#    UNIFORM
################################################################################
css('form.uniForm',
    css('.errorlist', overflow='hidden'),
    css('.legend', margin=cssv.uniform_padding),
    css('label'),
    css('.ctrlHolder,.buttonHolder',
        margin=0,
        overflow='hidden',
        padding=cssv.uniform.padding,
        vertical_align='middle'),
    css('.layout-element',
        margin = lambda: '0 0 {0}'.format(cssv.uniform.padding*1.5)))


#                   'buttonholder_padding': "10px 0",
#                   'error_color': '#af4c4c',
#                   'error_background': '#ffbfbf'

################################################################################
#    TABLE LAYOUT
################################################################################
css('table.uniFormTable',
    css('input[type="checkbox"]',
        float = 'none',
        margin = 0),
    css('th,td',
        padding = lambda: '{0}px 0 {0}px {0}px'.format(cssv.uniform.padding)),
    css('th:last-child,td:last-child',
        padding = cssv.uniform.padding),
    clearfix(),
    #process_elems(css('td.error')),
    css('td.error:last-child',
        padding = cssv.uniform.padding),
    table_layout = cssv.uniform.table_layout,
    width = '100%'
)
         
