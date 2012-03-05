'''Top bar styling
'''
from djpcms.style import css, gradient, radius, shadow, cssv
from . import defaults

cssv.declare_from_module(defaults)

############################################################
#    START THEME
start = cssv.theme_setter('start')
start.table_odd_background_color = '#f2f2f2'
start.table_even_background_color = 'transparent'
start.table_even_sort_background = '#fcefa1'
start.table_odd_sort_background = '#f7eeb5'


############################################################
#    SIRO THEME
siro = cssv.theme_setter('siro')
siro.table_odd_background_color = '#f2f2f2'
siro.table_even_background_color = 'transparent'
siro.table_even_sort_background = '#fbec88'
siro.table_odd_sort_background = '#f0e7ad'


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
    css('tbody td', vertical_align = 'center', padding = '4px'),
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

