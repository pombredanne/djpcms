'''Style inputs, widgets and forms used by djpcms.'''
from djpcms.media.style import *

################################################################################
##    VARIABLES
#
cssv.disabled.opacity = 0.7
cssv.disabled.cursor = 'not-allowed'
#
cssv.input.padding = px(4)
cssv.input.background = cssv.widget.body.background
cssv.input.color = cssv.widget.body.color
cssv.input.radius = cssv.clickable.radius
cssv.input.border.width = cssv.clickable.default.border.width
cssv.input.border.color = cssv.clickable.default.border.color
cssv.input.border.style = cssv.clickable.default.border.style
cssv.input.focus_color = None
cssv.input.focus_shadow = '0 3px 3px rgba(0,0,0,0.2)'
cssv.input.required_font_weight = 'None'
#
cssv.button.padding = spacing(cssv.input.padding, 9)
#
cssv.alert.background = color('#FCF8E3')
cssv.alert.color = color('#C09853')
cssv.alert.radius = cssv.body.radius
cssv.alert.border_color = lazy(color.darken, cssv.alert.background, 5)
cssv.alert_error.background = color('#F2DEDE')
cssv.alert_error.border_color = lazy(color.darken, cssv.alert_error.background, 5)
cssv.alert_error.color = color('#B94A48')
#
cssv.form.padding = cssv.input.padding # This controls the padding of all fields
cssv.form.table_layout = 'auto'
cssv.form.inlinelabels_width = pc(32)
#
cssv.definition_list.opacity = 0.8
cssv.definition_list.font_weight = 'normal'
################################################################################


################################################# CLEARINPUT
class clearinp(mixin):
    '''For clearing floats to all *elements*.'''    
    def __call__(self, elem):
        elem['outline'] = 'none'


################################################# WIDGET
css('.edit-menu',
    horizontal_navigation(float='right',
                          hover=bcd(text_decoration='none'),
                          padding=spacing(0,px(2))))


################################################# OBJECT DEFINITIONS
css('dl.object-definition',
    cssa(':first-child', margin_top = 0),
    css('dt',
        opacity(cssv.definition_list.opacity),
        font_weight=cssv.definition_list.font_weight,
        float='left',
        clear='left',
        width='40%',
        margin = 0),
    css('dd', margin = 0),
    cssa('.w20 dt', width='20%'),
    cssa('.w40 dt', width='40%'),
    cssa('.w50 dt', width='50%'),
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
    '''Consistent padding using the ``form_padding`` variable'''
    p = cssv.form.padding
    if elem.name == 'uniformtable-elems':
        data.update({'padding': '{0}px 0 {0}px {0}px'.format(p)})
    elif elem.name == 'uniformtable-errors':
        data.update({'padding': '0 0 0 {0}px'.format(p)})
    elif elem.name == 'uniform-errorlist':
        data.update({'margin': '{0}px 0 0'.format(p),
                     'padding': p})
    return data


############################################################    INPUTS
css('.field-widget',
    gradient(cssv.input.background),
    radius(cssv.input.radius),
    border(**cssv.input.border.params()),
    css('input[type="text"],input[type="password"],textarea,select',
        clearinp(),
        placeholder(cssv.input.placeholder_color),
        bcd(background=cssv.input.background, color=cssv.input.color),
        border='none',
        line_height=1,
        padding=spacing(cssv.input.padding.top, 0, cssv.input.padding.bottom),
        margin=0,
        width='100%'),
    css('select',
        padding=lazy(lambda: spacing(cssv.input.padding-px(1), 0))),
    css('input:focus,textarea:focus,select:focus', clearinp()),
    padding=spacing(0, cssv.input.padding))

css('.field-widget.focus',
    shadow(cssv.input.focus_shadow),
    border_color = cssv.input.focus_color)

for n in range(1,10):
    css('.field-widget.span{0}'.format(n),
         width = '{0}px'.format(size(n)))

############################################################    BUTTONS
#'button.button,a.button,input.button[type="submit"]'
buttons = 'input.button[type="submit"], button, a.button'
css(buttons,
    padding = cssv.button.padding,
    display='inline-block',
    margin_right=px(4))

css('button.large,a.button.large,input.button.large[type="submit"]',
    radius(cssv.input.radius),
    padding=2*cssv.input.padding)

css(disabled_selector,
    opacity(cssv.disabled.opacity),
    cursor =  cssv.disabled.cursor)


############################################################    ALERTS
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


############################################################    FORM
from djpcms.forms.layout import classes
css('form.%s' % classes.form,
    css('.errorlist,.form-messages', overflow='hidden', display='none'),
    css('.legend', margin=cssv.form.padding),
    css('label'),
    css('.%s' % classes.required,
        cssb('.%s' % classes.label,
             font_weight=cssv.input.required_font_weight)),
    # Inline labels
    css('.%s' % classes.inlineLabels,
        css('.%s' % classes.label,
            float='left',
            width=cssv.form.inlinelabels_width,
            margin=spacing(cssv.form.padding,pc(2),cssv.form.padding,0)),
        css('.field-widget',
            margin_left=lazy(lambda: cssv.form.inlinelabels_width+pc(2)),
            width='auto'),
        cssa('.%s'%classes.buttonHolder,
             padding_left=lazy(lambda: cssv.form.inlinelabels_width+pc(2)))),
    css('.%s' % classes.ctrlHolder,
        css('.%s'%classes.align_right,
            float='right'),
        css('.%s'%classes.align_middle,
            text_align='center',
            margin_right=0,
            margin_left=0),
        margin=0,
        overflow='hidden',
        padding=spacing(0, cssv.form.padding, cssv.form.padding),
        vertical_align='middle'),
    css('.layout-element',
        margin=lazy(lambda: spacing(0,0,cssv.form.padding*1.5))),
    css('.formRow',
        radius(cssv.alert.radius),
        css('table',
            css('td',
                css(buttons, width='100%'),
                cssa(':last-child',
                     css(buttons+',.field-widget',
                         radius(lambda: spacing(0,cssv.body.radius,cssv.body.radius,0))),
                     border='none'),
                cssa(':first-child',
                     css(buttons+',.field-widget',
                         radius(lambda: spacing(cssv.body.radius,0,0,cssv.body.radius)))),
                border_width=spacing(0,cssv.input.border.width,0,0),
                border_style='solid',
                border_color=cssv.button.border_color),
            table_layout='auto'),
        css('.field-widget',
            border='none'),
        css('table',
            width='100%'),
        css(buttons, radius(0), margin=0, border='none'),
        
        border_style='solid',
        border_width=cssv.input.border_width,
        border_color=cssv.button.border_color,
        padding=0,
        margin=0))


#                   'buttonholder_padding': "10px 0",
#                   'error_color': '#af4c4c',
#                   'error_background': '#ffbfbf'

################################################################################
#    TABLE LAYOUT
################################################################################
css('table.uniFormTable',
    css('input[type="checkbox"]', float='none', margin=0),
    css('th,td',
        padding=spacing(cssv.form.padding, 0, cssv.form.padding,
                        cssv.form.padding)),
    css('th:last-child, td:last-child',
        padding=cssv.form.padding),
    clearfix(),
    #process_elems(css('td.error')),
    css('td.error:last-child',
        padding = cssv.form.padding),
    table_layout = cssv.form.table_layout,
    width = '100%'
)
         
