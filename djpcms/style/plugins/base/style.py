'''Style inputs, widgets and forms used by djpcms 
'''
from djpcms.style import *

################################################################################
##    VARIABLES
cssv.panel.background = cssv.color.grayLighter
cssv.panel.border_color = color(RGBA(0,0,0,0.05))
cssv.panel.border_width = px(1)
cssv.panel.padding = spacing(px(6))

cssv.widget.hd.background = cssv.panel.background
cssv.widget.hd.font_size = cssv.heading.h3.font_size
cssv.widget.hd.line_height = cssv.heading.h3.line_height
cssv.widget.hd.font_weight = cssv.header.font_weight
cssv.widget.hd.text_transform = 'none'
cssv.widget.padding = cssv.panel.padding
cssv.widget.hd.padding = cssv.widget.padding
cssv.widget.bd.padding = cssv.widget.padding
cssv.widget.ft.padding = cssv.widget.padding
#
cssv.disabled.opacity = 0.7
cssv.disabled.cursor = 'not-allowed'
#
cssv.input.padding = px(4)
cssv.input.border_width = px(1)
cssv.input.border_color = cssv.color.grayLight
cssv.input.radius = cssv.body.radius
cssv.input.focus_color = None
cssv.input.focus_shadow = '0 3px 3px rgba(0,0,0,0.2)'
cssv.input.required_font_weight = 'None'
#
cssv.button.padding = spacing(cssv.input.padding, 9)
cssv.button.default.background = ('v',cssv.color.white,cssv.color.grayLighter)
cssv.button.hover.background = cssv.color.grayLighter
cssv.button.active.background = ('v',cssv.color.grayLighter,
                                 cssv.color.grayLight)
cssv.button.border_color = cssv.color.grayLight
#
cssv.alert.background = color('#FCF8E3')
cssv.alert.color = color('#C09853')
cssv.alert.radius = cssv.body.radius
cssv.alert.border_color = lazy(color.darken, cssv.alert.background, 5)
cssv.alert_error.background = color('#F2DEDE')
cssv.alert_error.border_color = lazy(color.darken, cssv.alert_error.background, 5)
cssv.alert_error.color = color('#B94A48')
#
cssv.uniform.padding = px(4)
cssv.uniform.table_layout = 'auto'
#
cssv.definition_list.opacity = 0.8
cssv.definition_list.font_weight = 'normal'
################################################################################


################################################# CLEARINPUT
class clearinp(mixin):
    '''For clearing floats to all *elements*.'''    
    def __call__(self, elem):
        elem['border'] = 'none'
        elem['outline'] = 'none'


################################################# WIDGET
css('.edit-menu',
    horizontal_navigation(float='right',
                          hover=bcd(text_decoration='none'),
                          padding=spacing(0,px(2))))

css('.widget',
    radius(cssv.body.radius),
    cssb('.hd',
         gradient(cssv.widget.hd.background),
         css('h1,h2,h3,h4,h5',
             font_size=cssv.widget.hd.font_size,
             font_weight=cssv.widget.hd.font_weight,
             text_transform=cssv.widget.hd.text_transform,
             line_height=cssv.widget.hd.line_height,
             float = 'left',
             padding = 0,
             margin = 0,
             background = 'transparent'
         ),
         css('.edit-menu',
             line_height=cssv.widget.hd.line_height),
         padding=cssv.widget.hd.padding,
         overflow='hidden',
    ),
    # we do this so that the attributes are after previous attributes
    cssb('.hd',
         padding_top=0,
         padding_bottom=0),
    cssb('.bd',
         padding=cssv.widget.bd.padding,
         overflow='hidden',
         border='none',
         display='block'),
    cssb('.ft',
         padding=cssv.widget.ft.padding,
         overflow='hidden',
         border='none')
)

################################################# BOX and PANEL
css('.panel,.box',
    radius(cssv.body.radius),
    border_style='solid',
    border_width=cssv.panel.border_width,
    border_color=cssv.panel.border_color)

css('.panel',
    gradient(cssv.panel.background),
    padding=cssv.panel.padding)


################################################# OBJECT DEFINITIONS
css('dl.object-definition',
    cssa(':first-child', margin_top = 0),
    css('dt',
        opacity(cssv.definition_list.opacity),
        font_weight=cssv.definition_list.font_weight,
        float = 'left',
        clear='left',
        width='40%',
        margin = 0),
    css('dd', margin = 0),
    cssa('.w20 dt', width = '20%'),
    cssa('.w40 dt', width = '40%'),
    cssa('.w50 dt', width = '50%'),
    overflow='hidden',
    margin='5px 0 0')

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
        line_height=1,
        padding=spacing(cssv.input.padding, 0),
        margin=0,
        width='100%',
        color='inherit',
        background='transparent'),
    css('input:focus,textarea:focus,select:focus', clearinp()),
    #css('select',
    #    css('option',_webkit_appearance='none'),
    #    _webkit_appearance='none'),
    radius(cssv.input.radius),
    padding=spacing(0, cssv.input.padding),
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
css('input.button[type="submit"], button.button',
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
    padding=2*cssv.input.padding)

css('.required label',
    font_weight = cssv.input_required_font_weight)

css(disabled_selector,
    opacity(cssv.disabled.opacity),
    cursor =  cssv.disabled.cursor)


################################################# ALERTS
css('.alert',
    gradient(cssv.alert.background),
    radius(cssv.alert.radius),
    cssa('.alert-error',
         gradient(cssv.alert_error.background),
         color=cssv.alert_error.color,
         border_color=cssv.alert_error.border_color),
    border_style='solid',
    border_width=px(1),
    border_color=cssv.alert.border_color,
    color=cssv.alert.color,
    padding='8px 35px 8px 14px')


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
         
