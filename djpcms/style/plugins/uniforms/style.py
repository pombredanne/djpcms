'''Uniform Styling
'''
from djpcms.style import css, mixin, cssv, radius, shadow, clearfix

################################################# CLEARINPUT
class clearinp(mixin):
    '''For clearing floats to all *elements*.'''    
    def __call__(self, elem):
        elem['border'] = 'none'
        elem['outline'] = 'none'


################################################################################
# Uniform variables
################################################################################
cssv.declare('input_radius',0)
cssv.declare('input_focus_color', None)
cssv.declare('input_focus_shadow', '0 3px 3px rgba(0,0,0,0.2)')
cssv.declare('input_required_font_weight',None)
cssv.declare('uniform_padding',4)
cssv.declare('uniform_table_layout','auto')


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
    radius(cssv.input_radius),
    padding = cssv.input_padding,
    border_size = cssv.input_border_size,
    focus_border_color = cssv.input_focus_color,
    input_focus_shadow = cssv.input_focus_shadow)

css('.field-widget.focus',
    shadow(cssv.input_focus_shadow),
    border_color = cssv.input_focus_color)



for n in range(1,10):
    css('.field-widget.span{0}'.format(n),
         width = '{0}px'.format(size(n)))


css('.required label',
    font_weight = cssv.input_required_font_weight)

css(disabled_selector,
    opacity = cssv.disabled_opacity,
    cursor =  cssv.disabled_cursor)


################################################################################
#    UNIFORM
################################################################################
css('form.uniForm',
    css('.errorlist', overflow='hidden'),
    css('.legend', margin=cssv.uniform_padding),
    css('label'),
    css('.ctrlHolder,.buttonHolder',
        clearfix(),
        margin = 0,
        overflow = 'hidden',
        padding = cssv.uniform_padding),
    css('.layout-element',
        margin = lambda: '0 0 {0}px'.format(int(cssv.uniform_padding*1.5))))


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
        padding = lambda: '{0}px 0 {0}px {0}px'.format(cssv.uniform_padding)),
    css('th:last-child,td:last-child',
        padding = cssv.uniform_padding),
    clearfix(),
    #process_elems(css('td.error')),
    css('td.error:last-child',
        padding = cssv.uniform_padding),
    table_layout = cssv.uniform_table_layout,
    width = '100%'
)
         
