'''Table'''
from djpcms.media.style import *
from djpcms.html.table import table_container_class

############################################################
cssv.table.padding = spacing(px(4))
cssv.table.line_height = cssv.body.line_height

cssv.table.odd_background_color = 'transparent'
cssv.table.even_background_color = 'transparent'
cssv.table.even_sort_background = None
cssv.table.odd_sort_background = None
cssv.table.border_color = None

cssv.table.head.font_size = None
cssv.table.head.font_weight = None
cssv.table.head.padding = cssv.table.padding


################################################################################
# SPECIAL CELL CLASSES
################################################################################
css('td.checkbox', text_align='center')
css('td.one-line', white_space='nowrap')
css('th.%s' % classes.clickable, radius(0))

################################################################################
# DATATABLE
################################################################################
border_width = cssv.clickable.default.border.width
css('.'+table_container_class,
    css('.dataTables_filter input',
        width = '200px',
        padding = '5px 5px',
        font_size = '110%'),
    css('table',
        css('tbody',
            border(color=cssv.clickable.default.border.color,
                   width=spacing(0, border_width),
                   style=cssv.clickable.default.border.style)),
        css('td',
            vertical_align='center',
            padding=cssv.table.padding,
            line_height=cssv.table.line_height),
        css('th',
            bcd(**cssv.clickable.default.params()),
            vertical_align='center',
            font_size=cssv.table.head.font_size,
            font_weight=cssv.table.head.font_weight,
            padding=cssv.table.head.padding,
            line_height=cssv.table.line_height),
        cssa('.nofooter',
             border(color=cssv.clickable.default.border.color,
                    width=spacing(0, 0, border_width),
                    style=cssv.clickable.default.border.style))),
    width=pc(100),
    display='none',
    text_align='left',
    margin=0,
    background='transparent')

css('.'+table_container_class,
    css('.clear',
        clearfix()),
    css('.DTTT_container',
        float='right',
        margin = '0 1em 1em 0'),
    css('.row-selector',
        float='left',
        margin=0),
    css('.col-selector',
        float='right',
        margin='0 0 1em'),
    css('.pagination',
        float='right'),
    css('.dataTables_info',
        float='left',
        margin='0 1em 0 0'),
    css('.dataTables_filter',
        float='right',
        margin='0.5em 0 0 0'),
    css('.dataTables_processing',
        float='left',
        margin='0 0 0 1em'))

#
#    row_selector_float = 'left',
#    row_selector_margin = '0',
#    #
#    col_selector_float = 'right',
#    col_selector_margin = '0 0 1em',
#    #
#    odd_background_color = cssv.table_odd_background_color,
#    even_background_color = cssv.table_even_background_color,
#    #
#    even_sort_background = cssv.table_even_sort_background,
#    odd_sort_background = cssv.table_odd_sort_background


css('.action-check',
    css('input', margin = '0 5px 0 0')
    )

