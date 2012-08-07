'''Table'''
from .base import *
from djpcms.html.table import table_container_class

############################################################
cssv.table.padding = spacing(px(4), px(6))
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
css('td.one-line', white_space='nowrap')
css('th.%s' % classes.clickable, radius(0))


css('table',
    css('th, td',
        padding=cssv.table.padding,
        line_height=cssv.table.line_height,
        vertical_align='center',
        text_align='left'))

################################################################################
# DATATABLE
################################################################################
border_width = cssv.clickable.default.border.width
css('.'+table_container_class,
    css('.dataTables_filter input',
        width = '200px',
        padding = '5px 5px',
        font_size = '110%'),
    #css('.dataTables_wrapper',
    #    overflow_x='auto'),
    css('table',
        css('tbody',
            bcd(**cssv.widget.body.params()),
            border(color=cssv.clickable.default.border.color,
                   width=spacing(0, border_width),
                   style=cssv.clickable.default.border.style)),
        css('th',
            bcd(**cssv.clickable.default.params()),
            font_size=cssv.table.head.font_size,
            font_weight=cssv.table.head.font_weight),
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
    css('.%s' % classes.widget_head,
        line_height=px(20)),
    css('.clear',
        clearfix(),
         margin_bottom=px(10)),
    css('.DTTT_container',
        float='right',
        margin=0),
    css('.row-selector',
        float='left',
        margin=0),
    css('.col-selector',
        float='right',
        margin=0),
    css('.pagination',
        float='right'),
    css('.dataTables_info',
        float='left',
        margin=0),
    css('.dataTables_length',
        float='left',
        margin=0),
    css('.dataTables_paginate',
        cssb('span',
             cssa(':first-child',
                 radius(radius_left)),
             cssa(':last-child',
                  radius(radius_right))),
        css('.paginate_button,.paginate_active',
            clickable_default(),
            padding=spacing(px(2),px(6)),
            cursor='pointer',
            margin=0),
        css('.paginate_active',
            bcd(**cssv.clickable.active.params())),
        float='right'),
    css('.dataTables_processing',
        float='left',
        margin=0),
    css('.dataTables_filter',
        float='right'))

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

