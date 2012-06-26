'''Table'''
from djpcms.media.style import *

############################################################
cssv.table.padding = spacing(px(4))
cssv.table.line_height = cssv.body.line_height

cssv.table.odd_background_color = 'transparent'
cssv.table.even_background_color = 'transparent'
cssv.table.even_sort_background = None
cssv.table.odd_sort_background = None


################################################################################
# SPECIAL CELL CLASSES
################################################################################
css('td.checkbox', text_align='center')
css('td.one-line', white_space='nowrap')


################################################################################
# DATATABLE
################################################################################
css('.data-table',
    css('.dataTables_filter input',
        width = '200px',
        padding = '5px 5px',
        font_size = '110%'),
    css('table.main'),
    css('th.sortable', cursor = 'pointer'),
    css('td,th',
        vertical_align='center',
        padding=cssv.table.padding,
        line_height=cssv.table.line_height),
    width = '100%',
    display = 'none',
    text_align = 'left',
    margin = '0',
    background='transparent',
    # head/tail
    head_border_color = '#fff',
    #'toolbox_background_color':'#fff',
    body_border_color = '#a6c9e2',
    head_padding = '4px',
    #
    toolbox_min_height = '40px',
    #
    head_border = '1px solid #a6c9e2',
    row_border = '1px solid transparent',
    #
    # Floating panels
    DTTT_float = 'right',
    DTTT_margin = '0 1em 1em 0',
    #
    pagination_float = 'right',
    #
    dataTables_info_float = 'left',
    dataTables_info_margin = '0 1em 0 0',
    #
    dataTables_filter_float = 'right',
    dataTables_filter_margin = '0.5em 0 0 0',
    #
    processing_float = 'left',
    processing_margin = '0 0 0 1em',
    #
    row_selector_float = 'left',
    row_selector_margin = '0',
    #
    col_selector_float = 'right',
    col_selector_margin = '0 0 1em',
    #
    odd_background_color = cssv.table_odd_background_color,
    even_background_color = cssv.table_even_background_color,
    #
    even_sort_background = cssv.table_even_sort_background,
    odd_sort_background = cssv.table_odd_sort_background
)

css('.action-check',
    css('input', margin = '0 5px 0 0')
    )

