'''Style inputs, widgets and forms used by djpcms.'''
from djpcms.media.style import *
from djpcms.forms.layout import classes

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
cssv.input.focus_shadow = '0 0 5px rgba(0,0,0,0.2)'
cssv.input.required_font_weight = 'None'
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
cssv.form.legend.radius = cssv.body.radius
cssv.form.legend.padding = spacing(5, 10)
cssv.form.legend.background = cssv.color.offwhite
cssv.form.legend.color = cssv.body.color
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


disabled_selector = '''\
.disabled .{0}, .readonly .{0},
input[disabled], select[disabled], textarea[disabled],
input[readonly], select[readonly], textarea[readonly]
'''.format(classes.ui_input)

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
css('.%s' % classes.ui_input,
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
    padding=spacing(0, cssv.input.padding),
    width='auto')

css('.%s.focus' % classes.ui_input,
    shadow(cssv.input.focus_shadow),
    border_color=cssv.input.focus_color)

for n in range(1,10):
    css('.%s.span%s' % (classes.ui_input, n),
         width=px(size(n)))

css(disabled_selector,
    opacity(cssv.disabled.opacity),
    cursor=cssv.disabled.cursor)

########################################################    CHECKBOX AND RADIO
css('label',
    display='block')
css('.checkbox, .radio',
    padding_left=px(18),
    padding_top=px(5),
    line_height='normal')
css('.checkbox input[type="checkbox"],.radio input[type="radio"]',
    float='left',
    margin_left='-18px',
    display='inline-block',
    cursor='pointer',
    line_height='normal',
    margin_bottom=0)
css('.radio.inline, checkbox.inline',
    display='inline-block',
    vertical_align='middle')
css('.radio.inline + .radio.inline, checkbox.inline + .checkbox.inline',
    margin_left=px(10))

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
css('form.%s' % classes.form,
    css('.errorlist,.form-messages', overflow='hidden', display='none'),
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
        css('.%s' % classes.control,
            margin_left=lazy(lambda: cssv.form.inlinelabels_width+pc(2))),
        cssa('.%s' % classes.button_holder,
             padding_left=lazy(lambda: cssv.form.inlinelabels_width+pc(2)))),
    css('.inline',
        display='inline-block'),
    css('.inline + .inline',
        margin_left=px(10)),
    # Block labels
    css('.%s' % classes.blockLabels,
        css('.%s' % classes.label,
            margin_bottom=px(5))),
    #
    # legend
    css('.%s' % classes.legend,
        bcd(**cssv.form.legend.params()),
        radius(cssv.form.legend.radius),
        margin=spacing(0, cssv.form.padding, cssv.form.padding),
        padding=cssv.form.legend.padding),
    #
    # Control holder
    css('.%s' % classes.ctrlHolder,
        clearfix(),
        css('.%s' % classes.align_right,
            float='right'),
        css('.%s' % classes.align_middle,
            text_align='center',
            margin_right=0,
            margin_left=0),
        margin=0,
        padding=spacing(0, cssv.form.padding, cssv.form.padding),
        vertical_align='middle'),
    css('.layout-element',
        margin=lazy(lambda: spacing(0,0,cssv.form.padding*1.5)))
    )


################################################################################
#    TABLE LAYOUT
################################################################################
css('table.uniFormTable',
    css('input[type="checkbox"]', float='none', margin=0),
    css('th, td',
        padding=cssv.form.padding),
    css('th + th, td + td',
        padding=spacing(cssv.form.padding, cssv.form.padding,
                        cssv.form.padding, 0)),
    clearfix(),
    css('td.error',
        padding_top=0,
        padding_bottom=0),
    table_layout = cssv.form.table_layout,
    width = '100%'
)
css('.%s' % classes.nolabel,
    cssb('table.uniFormTable thead', display='none'))

############################################################    TEXTAREA
css('textarea.taboverride',
    font_family='monospace')
