from medplate.css import CssContext, CssTheme, jquery_style_mapping

from .elements import *

# SOME DEFAULTS
BOX_HEADER_PADDING = '6px 5px'
BOX_BODY_PADDING = '5px 5px'


CssContext('field-widget-input',
           tag = '.field-widget.input',
           template = 'medplate/field-widget.css_t',
           data = {
                   'padding': '0.3em'
                   }
)

CssContext('float_right', tag = '.right', data = {'float':'right'})

#________________________________________ ANCHOR
CssContext('button-submit',
           tag = 'input.ui-button',
           data = {
                   'padding': '0.3em 0.5em'
                   }
)

CssContext('anchor',
           tag = 'a',
           template = 'medplate/anchor.css_t',
           data = {
                   'text_decoration': 'none',
                   'weight':'normal',
        }
)

                    
#________________________________________ nav    -     MAIN NAVIGATION
CssContext('nav',
           tag='ul.main-nav',
           template='medplate/horizontal_navigation.css_t',
           process = horizontal_navigation,
           data = {
                   'display':'block',
                   'anchor_horizontal_padding': 20,
                   # Useful! Control the with of drop-down
                   'secondary_anchor_width': 150,
                   'secondary_border_with': 1,
                   'hover_background':'transparent',
                   'height': '2.5em',
                   'inner_height': '2.5em',
                   'list_margin': '0',
                   'secondary_radius':0}
           )


#________________________________________ PAGINATION
CssContext('paginator',
           tag = 'div.jquery-pagination',
           template = 'medplate/pagination.css_t',
           data = {
                   'navigator_float':'left',
                   'navigator_height':'30px',
                   'information_float':'right',
                   'information_height':'20px',
                   'padding':'0 0 10px 0'
                   }
           )


#________________________________________ FORM & UNIFORMS
CssContext('uniform',
           tag = 'form.uniForm',
           template = 'medplate/uniform.css_t',
           data = {
                   'background':'transparent',
                   'text_align':'left',
                   'table_padding': '2px 5px 2px 0',
                   'buttonholder_padding': "10px 0",
                   'error_color': '#af4c4c',
                   'error_background': '#ffbfbf'
                   },
           elems = [CssContext('uniform-disabled',
                        tag = '.disabled',
                        data = {
                         'opacity': 0.6,
                         }
                    )
                    ]
           )
CssContext('uniformHint',
           tag = '.formHint',
           parent = 'uniform',
           data = {'display':'none'}
           )
CssContext('label',
           tag = ' label',
           parent = 'uniform'
           )
CssContext('tablerelated-legend',
           tag = '.tablerelated .legend'
)
CssContext('tablerelated-header',
           tag = '.tablerelated thead span.required',
           data = {
                'font_weight':'bold'
        }
)
           

#________________________________________ SUBMITS AND BUTTONS
CssContext('button',
           tag = '.ui-button.ui-widget',
           data = {
            'font_weight':'bold',
            }
)
CssContext('minibutton',
           tag = '.minibutton',
           data = {
            'font_size':'90%'
        })


#________________________________________ Simple Horizontal navigation
CssContext('horizontal-list',
           tag = '.horizontal li',
           data = {
                'margin':'0 5px',
                'display':'inline'
            },
           elems = [CssContext(
                'horizontal-list-buttons',
                tag = 'button',
                data = {
                        'margin':'0 0 5px'
                })
                ]
    )
CssContext('model-links',
           tag = 'ul.asbuttons.model-links li',
           data = {
                'margin':'0'
                }
           )

CssContext('user-nav', tag = '.user-nav')

#________________________________________ TAGS
CssContext('tags',
           tag='div.tagindex',
           template='medplate/tags.css_t',
           data = {
                   'background': 'transparent',
                   'text_align': 'justify',
                   'tag_opacity': 0.7}
           )

#________________________________________ OBJECT DEFINITIONS
CssContext('object_definitions',
           tag='div.object-definition',
           template='medplate/object-definition.css_t',
           process = object_definition,
           data = {
                   'text_align':'left',
                   'left_width':30
                   }
           )

#________________________________________ DATATABLE
CssContext('datatable',
           tag='.data-table',
           template='medplate/datatable.css_t',
           data = {
                   'width':'100%',
                   'display':'none',
                   'text_align': 'left',
                   'margin': '0 0 15px',
                   'background': 'transparent',
                   # head/tail
                   'head_border_color':'#fff',
                   #'toolbox_background_color':'#fff',
                   'body_border_color':'#a6c9e2',
                   'head_padding': '4px',
                   #
                   'toolbox_min_height':'40px',
                   #
                   'head_border': '1px solid #a6c9e2',
                   'row_border':'1px solid transparent',
                   #
                   # Floating panels
                   'DTTT_float':'right',
                   'DTTT_margin':'0 1em 1em 0',
                   #
                   'pagination_float':'right',
                   #
                   'dataTables_info_float':'left',
                   'dataTables_info_margin':'0 1em 0 0',
                   #
                   'dataTables_filter_float':'right',
                   'dataTables_filter_margin':'0.5em 0 0 0',
                   #
                   'processing_float':'left',
                   'processing_margin':'0 0 0 1em',
                   #
                   'row_selector_float':'left',
                   'row_selector_margin':'0',
                   #
                   'col_selector_float':'right',
                   'col_selector_margin':'0 0 1em'
                   },
           elems = [CssContext('datatable-title',
                               tag = 'h3.table-title',
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

#________________________________________ blockelement
CssContext('blockelement',
           tag = '.djpcms-block-element, .edit-block',
           data = {
                   'margin': '0 0 20px 0',
                   'display': 'block'
                   }
           )

CssContext('blockelement_preview',
           tag = '.edit-block .preview .djpcms-block-element',
           data = {
                   'margin': '0'
                   }
           )

CssContext('edit_plugin_body',
           tag = '.edit-block .bd.plugin-form'
           )

#________________________________________ BOX
box = CssContext('box',
                 tag='.djpcms-html-box',
                 template='medplate/box/box.css_t',
                 data = {},
                 elems = [
                    CssContext(
                        'box-hd',
                        tag='.hd',
                        data={'padding':BOX_HEADER_PADDING,
                              'overflow':'hidden'},
                        elems = [
                            CssContext(
                                'box-hd-h2',
                                tag='h2',
                                data={#'text_transform':'uppercase',
                                      'font_size':'110%',
                                      'font_weight':'normal',
                                      'float':'left',
                                      'padding':'0',
                                      'margin':'0'},
                                )
                        ]),
                    CssContext('box-bd',
                               tag='.bd',
                               data={'padding':BOX_BODY_PADDING,
                                     'border':'none'}),
                    CssContext('box-ft',
                               tag='.ft',
                               data={'padding':BOX_BODY_PADDING,
                                     'overflow':'hidden',
                                     'border':'none'})
                    ]
)


#________________________________________ EDITING
editbox = CssContext('editbox',
           parent = box,
           same_as_parent = True,
           tag='.edit-block',
           template='medplate/box/editbox.css_t',
           data = {'padding':'0',
                   'border': 'none'})

CssContext('editboxft',
           parent = editbox,
           tag=' > .ft',
           data={'padding':'0',
                 'overflow':'hidden',
                 'border':'none'})


CssContext('bodyedit',
           tag = 'body.admin',
           template='medplate/editing.css_t',
           data = {
                   'placeholder_border': '2px dashed #666'
                   }
           )


CssContext('element',
           tag='div.flat-element',
           data = {'overflow':'hidden',
                   'padding':0}
           )


#________________________________________ PANEL
CssContext('panel',
           tag='div.flat-panel',
           data = {'overflow':'hidden',
                   'margin':0,
                   'padding':'7px 7px'}
           )

#________________________________________ FLAT BOX
CssContext('flatbox',
           tag='div.flat-box',
           template='medplate/box/box.css_t',
           data = {'overflow':'hidden',
                   'margin':0,
                   'padding':0},
           elems = [CssContext('flatbox-hd',
                            tag='div.hd',
                            data={'padding':BOX_HEADER_PADDING,
                                  'overflow':'hidden'},
                            elems = [
                            CssContext(
                                'fltbox-hd-h2',
                                tag='h2',
                                data={#'text_transform':'uppercase',
                                      'font_size':'110%',
                                      'font_weight':'normal',
                                      'float':'left',
                                      'padding':'0',
                                      'margin':'0'},
                                )
                            ]),
                    CssContext('flatbox-bd',
                            tag='div.bd',
                            data={'padding':BOX_BODY_PADDING})
                    ]
           )


#________________________________________ FLAT BOX
CssContext('title-list',
           tag='.title-list .hd',
           data = {
            'margin':'0 0 10px'
        }
)
           
#________________________________________ PLAIN TABLE
CssContext('table',
           template='medplate/table.css_t',
           tag='table.plain',
           data = {'margin':'10px 0 15px',
                   'cell_padding': '3px 15px 3px 0',
                   'header_font_weight': 'bold',
                   'first_column_font_weight':'bold'}
           )


#________________________________________ SEARCH BOX
CssContext('search',
           tag='div.cx-search-bar',
           template='medplate/search-box.css_t',
           data = {
                'background':'#fff'
        }
)


#________________________________________ JQUERY UI-TABS
CssContext('tabs',
           tag='.ui-tabs',
           template='medplate/tabs.css_t'
           )


#________________________________________ MESSAGE LIST
CssContext('messagelist_ul',
           tag='ul li.messagelist',
           data = {
                   'margin':'0 0 5px',
                   }
           )
CssContext('messagelist',
           tag='ul li.messagelist',
           data = {
                   'margin':'0 0 3px',
                   'padding':'4px 12px'
                   }
           )


#________________________________________ BREADCRUMBS
CssContext('breadcrumbs',
           tag = 'div.breadcrumbs',
           template = 'medplate/breadcrumbs.css_t',
           data = {
                   'font_size': '130%',
                   'padding': '10px 0'}
           )


#________________________________________ JAVASCRIPT LOGGING PLUGIN
CssContext('jslog',
           tag = '.djp-logging-panel',
           data = {
                   'overflow': 'auto',
                   'height':'400px'},
           elems = [CssContext('jslog-debug',
                               tag = '.log.debug',
                               data = {'color':'#9C9C9C'}),
                    CssContext('jslog-info',
                               tag = '.log.info',
                               data = {'color':'#339933'}),
                    CssContext('jslog-warn',
                               tag = '.log.warn',
                               data = {'color':'#996633'}),
                    CssContext('jslog-error',
                               tag = '.log.error',
                               data = {'color':'#CC0033','font_weight':'bold'}),
                    CssContext('jslog-critical',
                               tag = '.log.critical',
                               data = {'color':'#CC0033','font_weight':'bold'})]
           )
CssContext('javascript_logging_paragraph',
           tag = '.djp-logging-panel pre',
           data = {
                   'font_family': 'monospace',
                   'font_size': '80%',
                   'text_align': 'left',
                   'margin':'0'
        }
)

#________________________________________ TABOVERRIDE
CssContext('taboverride',
           tag = 'textarea.taboverride',
           data = {
                   'font_family': 'monospace',
                   'margin':'0'
                   }
           )


#________________________________________ Text Select
CssContext('textselect',
           tag = 'div.text-select .target',
           data = {
                   'display': 'none',
                   'margin':'0'
                   }
           )


#________________________________________ bsmSelect
CssContext('bsmselect',
           tag = '.bsmContainer',
           template = 'medplate/bsmselect.css_t',
           data = {}
           )


#________________________________________ PAGINATION
CssContext('pagination_item',
           tag = '.pagination-item',
           data = {
            'margin':'0 0 20px',
            'padding': '10px'
            }
           )

#________________________________________ SPECIAL IDS AND CLASSES
CssContext('server_exception',
           tag = '.server-exception',
           data = {'padding': '20px'}
           )

CssContext('content',tag='#content',
           data={'min_height':'500px',
                 'overflow':'hidden',
                 'padding':'0 0 20px 0',
                 'text_align':'left'})
CssContext('hidecontent',tag='.djph',data={'display':'none'})



default_data_theme = (
          ('body',{'color':'#222222',
                   'background':'#ffffff'}),
          ('flatbox', {'background':'#ffffff',
                      'border':'1px solid #4297d7'}),
          ('breadcrumbs', {'color':'#333333'}),
          ('box',{}),
          # Uniform
          ('uniform label',{'font_weight': 'bold',
                           'color': '#666666'}),
          ('tablerelated-legend', {'font_size': '110%',
                                  'font_weight':'bold'
                                  }),
           # dataTable
           ('datatable', {'odd_background_color':'#f2f2f2',
                         'even_background_color':'transparent',
                         'even_sort_background':'#fcefa1',
                         'odd_sort_background':'#f7eeb5'}),
           #
           # Navigation
          ('nav', {'main_text_shadow': '0 2px 2px rgba(0, 0, 0, 0.5)',
                  'secondary_text_shadow': 'none',
                  # SHADOW OF DROP DOWN MENU
                  'secondary_border_color':'#b4b4b4',
                  'drop_down_shadow': '10px 10px 5px rgba(0,0,0, .5)',
                  'font_weight': 'bold',
                  'color': '#E7E5E5',
                  'background':'transparent',
                  'hover_background':'#79c9ec',
                  'secondary_hover_background':'#c2c2c2',
                  #'active_background':'#dcdcdc',
                  #'active_color':'#dcdcdc',
                  'hover_color': '#444',
                  'selected_color':'#444',
                  #'padding': '2px 0',     # Padding for outer ul
                  'height': '30px',
                  'list_margin': '0 5px',
                  'anchor_padding': '0 20px',
                  # Set the radius
                  'inner_radius': '10px',
                  'radius': '14px'}),
           ('edit_plugin_body', {'background':'#BAE28D'})
           )
