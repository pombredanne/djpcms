'''Uniform Styling
'''
from djpcms.style import css, cssv

################################################################################
# Uniform variables
################################################################################
cssv.declare('input_radius',0)
cssv.declare('input_focus_color',None)
cssv.declare('input_focus_shadow',shadow('0 3px 3px rgba(0,0,0,0.2)'))
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
    padding = cssv.input_padding,
    radius = radius(cssv.input_radius),
    border_size = cssv.input_border_size,
    focus_border_color = cssv.input_focus_color,
    input_focus_shadow = cssv.input_focus_shadow)

for n in range(1,10):
    CssContext('field-widget-span{0}'.format(n),
               tag = '.field-widget.span{0}'.format(n),
               data = {'width':'{0}px'.format(size(n))})


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
    clearfix(css('.ctrlHolder,.buttonHolder',
             margin = 0,
             overflow = 'hidden',
             padding = cssv.uniform_padding)),
    css('.layout-element',
        margin = '0 0 {0}px'.format(int(1.5*cssv.uniform_padding))))


#                   'buttonholder_padding': "10px 0",
#                   'error_color': '#af4c4c',
#                   'error_background': '#ffbfbf'

################################################################################
#    TABLE LAYOUT
################################################################################
clearfix(
         css('table.uniFormTable',
             css('input[type="checkbox"]',
                 float = 'none',
                 margin = 0),
             css('th,td',
                 padding = lambda: '{0}px 0 {0}px {0}px'.format(\
                                                cssv.uniform_padding.value)),
             css('th:last-child,td:last-child',
                 padding = cssv.uniform_padding),
             process_elems(css('td.error')),
             css('td.error:last-child',
                 padding = lambda: table_last_child_padding),
             table_layout = cssv.uniform_table_layout,
             width = '100%')
         ).css()
         
