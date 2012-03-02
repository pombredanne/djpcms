'''Top bar styling
'''
from medplate import CssContext, CssTheme, gradient, radius, shadow, variables
from . import defaults

variables.declare_from_module(defaults)


################################################################################
# SPECIAL CELL CLASSES
################################################################################
css('td.checkbox', text_align='center')
css('td.one-line', white_space='nowrap')


################################################################################
# DATATABLE
################################################################################
css('.data-table',
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
    odd_background_color = vars.table_odd_background_color,
    even_background_color = vars.table_even_background_color,
    #
    even_sort_background = vars.table_even_sort_background,
    odd_sort_background = vars.table_odd_sort_background
)

css('h3.table-title',
                               data = {
                                'padding':'4px',
                                'margin':'0',
                                'font-size':'110%'
                            }),
                    CssContext('datatable_filter_input',
                               tag ='.dataTables_filter input',
                               data = {'width': '200px',
                                       'padding': '5px 5px',
                                       #'border':'1px solid'},
                                       'font_size':'110%'
                            }),
                    CssContext('datatable_table',
                               tag='table.main',
                               data = {
                            }),
                    CssContext('datatable_thead',
                               tag='th.sortable',
                               data = {
                                'cursor': 'pointer'
                            }),
                    CssContext('datatable-tbody-td',
                               tag='tbody td',
                               data = {
                                'vertical_align': 'center',
                                'padding':'4px'
                            }),
                    ]
           )


CssContext('action-check',
           tag = '.action-check',
           elems = CssContext(
                    'action-check-input',
                     tag = 'input',
                     data = {
                        'margin':'0 5px 0 0'
                    })
           )

