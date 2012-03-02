'''Uniform Styling
'''
from djpcms.style import css, vars

################################################################################
# Uniform variables
################################################################################
variables.declare('input_radius',0)
variables.declare('input_focus_color',None)
variables.declare('input_focus_shadow',shadow('0 3px 3px rgba(0,0,0,0.2)'))
variables.declare('input_required_font_weight',None)
variables.declare('uniform_padding',4)
variables.declare('uniform_table_layout','auto')


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
    p = variables.uniform_padding.value
    if elem.name == 'uniformtable-elems':
        data.update({'padding': '{0}px 0 {0}px {0}px'.format(p)})
    elif elem.name == 'uniformtable-errors':
        data.update({'padding': '0 0 0 {0}px'.format(p)})
    elif elem.name == 'uniformtable-errors-last':
        data.update({'padding': '0 {0}px'.format(p)})
    elif elem.name == 'uniform-errorlist':
        data.update({'margin': '{0}px 0 0'.format(p),
                     'padding': p})
    elif elem.name == 'uniform-layout-element':
        m = int(1.5*p)
        data.update({'margin': '0 0 {0}px'.format(m)})
    return data
        
        
################################################################################
#    INPUT FIELDS
################################################################################
css('.field-widget',
    padding = variables.input_padding,
    radius = radius(variables.input_radius),
    border_size = variables.input_border_size,
    focus_border_color = variables.input_focus_color,
    input_focus_shadow = variables.input_focus_shadow)

for n in range(1,10):
    CssContext('field-widget-span{0}'.format(n),
               tag = '.field-widget.span{0}'.format(n),
               data = {'width':'{0}px'.format(size(n))})


css('.required label',
    font_weight = variables.input_required_font_weight)

css(disabled_selector,
    opacity = variables.disabled_opacity,
    cursor =  variables.disabled_cursor)


################################################################################
#    UNIFORM
################################################################################
CssContext('uniform',
           tag = 'form.uniForm',
           template = 'medplate/uniform.css_t',
           data = {
                   'background':'transparent',
                   'text_align':'left',
                   'buttonholder_padding': "10px 0",
                   'error_color': '#af4c4c',
                   'error_background': '#ffbfbf'
                   },
           elems = [CssContext('uniform-errorlist',
                        tag = '.errorlist',
                        data = {'overflow': 'hidden'},
                        process = process_elems
                    ),
                    CssContext('uniform-layout-element',
                        tag = '.layout-element',
                        process = process_elems
                    )]
           )
CssContext('uniform-holder',
           tag = 'form.uniForm .ctrlHolder, form.uniForm .buttonHolder',
           data = {
            'margin': '0',
            'clear': 'both',
            'overflow': 'hidden',
            'padding': variables.uniform_padding
            })           
CssContext('uniformHint',
           tag = '.formHint',
           parent = 'uniform',
           data = {'display':'none'}
           )
CssContext('label',
           tag = ' label',
           parent = 'uniform'
           )

################################################################################
#    TABLE LAYOUT
################################################################################
CssContext('uniformtable',
           tag = 'table.uniFormTable',
           data = {
            'table-layout': variables.uniform_table_layout,
            'width': '100%'
            },
           elems = [
            CssContext('uniformtable-checkbox',
                       tag = 'input[type="checkbox"]',
                       data = {'float':'none',
                               'margin': 0}),
            CssContext('uniformtable-td',
                       tag = 'td',
                       data = {})
        ])
CssContext('uniformtable-elems',
           tag = 'table.uniFormTable th, table.uniFormTable td',
           process = process_elems)
CssContext('uniformtable-elems-last',
           tag = 'table.uniFormTable th:last-child,\
 table.uniFormTable td:last-child',
           data = {
            'padding':variables.uniform_padding
            })
CssContext('uniformtable-errors',
           tag = 'table.uniFormTable td.error',
           process = process_elems)
CssContext('uniformtable-errors-last',
           tag = 'table.uniFormTable td.error:last-child',
           process = process_elems)
################################################################################
#    LEGEND
################################################################################
CssContext('uniform-legend',
           tag = '.uniForm .legend',
           data = {
            'margin': variables.uniform_padding
        }
)
