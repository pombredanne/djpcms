from medplate import CssContext

from .elements import *

# SOME DEFAULTS
BOX_HEADER_PADDING = '6px 12px'
BOX_BODY_PADDING = '5px 5px'

#________________________________________ ANCHOR
CssContext('anchor',
           tag = 'a',
           template = 'djpcms/style/anchor.css_t',
           data = {
                   'text_decoration': 'none',
                   'weight':'normal',
        }
)
CssContext('float_right',
           tag = '.right',
           data = {
                   'float':'right',
                   }
)


CssContext('anchor-ui',
           tag = 'a.ui-hoverable',
           data = {
            'display':'inline',
            'border':'none',
            'width':'18px',
            'height':'18px',
        }
)


#________________________________________ horizontal_list    -    HORIZONTAL LIST
CssContext('horizontal_list',
           tag = '.horizontal li',
           data = {
                   'display':'inline',
                   'margin':'0 5px'
                   }
)

CssContext('widget-anchor',
           tag = '.ui-widget-content a',
           template = 'djpcms/style/anchor.css_t',
           data = {
                   'text_decoration': 'none',
                   'weight':'normal',
                   }
           )
                    
#________________________________________ nav    -     MAIN NAVIGATION
CssContext('nav',
           tag='ul.main-nav',
           template='djpcms/style/horizontal_navigation.css_t',
           process = horizontal_navigation,
           data = {
                   'display':'block',
                   'anchor_horizontal_padding': 20,
                   'secondary_anchor_width': 150,       # Useful! Control the with of drop-down
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
           template = 'djpcms/style/pagination.css_t',
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
           template = 'djpcms/style/uniform.css_t',
           data = {
                   'background':'transparent',
                   'text_align':'left',
                   'table_padding': '2px 5px 2px 0',
                   'buttonholder_padding': "10px 0",
                   'error_color': '#af4c4c',
                   'error_background': '#ffbfbf'
                   }
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

CssContext('field-widget-input',
           tag = '.field-widget.input',
           template = 'djpcms/style/field-widget.css_t',
           data = {
                   'padding': '3px 3px'
                   }
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
#CssContext('button',
#           tag = '.ui-button',
#           template='djpcms/style/button.css_t',
#           data = {
#             'padding':'0.1em 0.3em',
#             'line_height':'1.2em'
#            }
#)

#________________________________________ TAGS
CssContext('tags',
           tag='div.tagindex',
           template='djpcms/style/tags.css_t',
           data = {
                   'background': 'transparent',
                   'text_align': 'justify',
                   'tag_opacity': 0.7}
           )

#________________________________________ OBJECT DEFINITIONS
CssContext('object_definitions',
           tag='div.object-definition',
           template='djpcms/style/object-definition.css_t',
           process = object_definition,
           data = {
                   'text_align':'left',
                   'left_width':30
                   }
           )


#________________________________________ TABLESORTER
CssContext('tablesorter',
           tag='table.tablesorter',
           template='djpcms/style/tablesorter.css_t',
           data = {
                   'width':'100%',
                   'text_align': 'left',
                   'margin': '0 0 15px',
                   'background': 'transparent',
                   # head/tail
                   'odd_background_color':'#ccc',
                   'head_border_color':'#fff',
                   #'toolbox_background_color':'#fff',
                   'body_border_color':'#a6c9e2',
                   'head_padding': '4px',
                   #
                   'toolbox_min_height':'40px',
                   #
                   'head_border': '1px solid #a6c9e2',
                   'row_border':'1px solid transparent'
                   }
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
                 tag='div.djpcms-html-box',
                 template='djpcms/style/box/box.css_t',
                 data = {'padding':'2px',
                         'border': 'none'})

CssContext('hd',
           parent = box,
           tag='.hd',
           template='djpcms/style/box/header.css_t',
           data={'padding':BOX_HEADER_PADDING,
                 #'text_transform':'uppercase',
                 'title_size':'110%',
                 'font_weight':'normal',
                 'overflow':'hidden'}),
CssContext('bd',
           parent = box,
           tag='.bd',
           data={'padding':BOX_BODY_PADDING,
                 'border':'none'}),
CssContext('ft',
           parent = box,
           tag='.ft',
           data={'padding':BOX_BODY_PADDING,
                 'overflow':'hidden',
                 'border':'none'})


#________________________________________ EDITING
editbox = CssContext('editbox',
           parent = box,
           same_as_parent = True,
           tag='.edit-block',
           template='djpcms/style/box/editbox.css_t',
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
           template='djpcms/style/editing.css_t',
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
           template='djpcms/style/box/box.css_t',
           data = {'overflow':'hidden',
                   'margin':0,
                   'padding':0},
           elems = [CssContext('hd',
                               tag='div.hd',
                               template='djpcms/style/box/header.css_t',
                               data={'font_weight': 'bold',
                                     'title_size':'110%',
                                     'padding':BOX_HEADER_PADDING,
                                     'overflow':'hidden'}),
                    CssContext('bd',
                               tag='div.bd',
                               data={'padding':BOX_BODY_PADDING})
                    ]
           )


#________________________________________ PLAIN TABLE
CssContext('table',
           template='djpcms/style/table.css_t',
           tag='table.plain',
           data = {'margin':'10px 0 15px',
                   'cell_padding': '3px 15px 3px 0',
                   'header_font_weight': 'bold',
                   'first_column_font_weight':'bold'}
           )


#________________________________________ SEARCH BOX
CssContext('search',
           tag='div.cx-search-bar',
           template='djpcms/style/search-box.css_t',
           data = {
                'background':'#fff'
        }
)


#________________________________________ JQUERY UI-TABS
CssContext('tabs',
           tag='.ui-tabs',
           template='djpcms/style/tabs.css_t'
           )


#________________________________________ MESSAGE LIST
CssContext('messagelist',
           tag='ul.messagelist li',
           data = {
                   'margin':'0 0 3px',
                   'padding':'4px 12px'}
           )


#________________________________________ BREADCRUMBS
CssContext('breadcrumbs',
           tag = 'div.breadcrumbs',
           template = 'djpcms/style/breadcrumbs.css_t',
           data = {
                   'font_size': '130%',
                   'padding': '10px 0'}
           )


#________________________________________ JAVASCRIPT LOGGING PLUGIN
CssContext('javascript_logging',
           tag = '.djp-logging-panel',
           data = {
                   'overflow': 'scroll',
                   'height':'400px'}
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
