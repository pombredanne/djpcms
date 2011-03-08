from medplate import CssContext

from .elements import horizontal_navigation

#________________________________________ ANCHOR
CssContext('anchor',
           tag = 'a',
           template = 'medplate/anchor.css_t',
           data = {
                   'text_decoration': 'none',
                   'weight':'normal',
                   'color':'#33789C',
                   'background': 'transparent',
                   'color_hover':'#204C64',
                   'background_hover':None
                   }
           )

                    
#________________________________________ MAIN NAVIGATION
CssContext('nav',
           tag='ul.main-nav',
           template='djpcms/style/horizontal_navigation.css_t',
           process = horizontal_navigation,
           data = {
                   'anchor_horizontal_padding': 20,
                   'secondary_anchor_width': 100,
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
                   'margin':'0 0 10px 0'
                   }
           )


#________________________________________ UNIFORM
CssContext('uniform',
           tag = 'form.uniForm',
           template = 'djpcms/style/uniform.css_t',
           data = {
                   'background':'transparent',
                   'input_border':'1px solid #ccc',
                   'input_padding': '3px 3px',
                   'table_padding': '2px 5px 2px 0',
                   'buttonholder_padding': "10px 0",
                   'error_color': '#af4c4c',
                   'error_background': '#ffbfbf'
                   }
           )


#________________________________________ SUBMITS AND BUTTONS
#CssContext('submit',
#           tag = 'input[type="submit"]',
#           template = 'djpcms/style/submit.css_t',
#           data = {
#                   'background':'#FFFFFF',
#                   'border':'1px solid #aaa',
#                   'text_align':'center',
#                   'padding': '3px 5px',
#                   'min_width': '50px'
#                   }
#           )

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
           data = {
                   'background': 'transparent'
                   }
           )


#________________________________________ TABLESORTER
CssContext('tablesorter',
           tag='table.tablesorter',
           template='djpcms/style/tablesorter.css_t',
           data = {
                   'width':'100%',
                   'text_align': 'left',
                   'margin': '10px 0 15px',
                   'background': 'transparent',
                   # head/tail
                   'odd_background_color':'#ccc',
                   'head_border_color':'#fff',
                   'body_border_color':'#a6c9e2',
                   'head_border': 'none',
                   'head_padding': '4px',
                   }
           )


#________________________________________ BOX
box = CssContext('box',
                 tag='div.djpcms-html-box',
                 template='djpcms/style/box/box.css_t',
                 data = {'padding':'2px',
                         'border': 'none'})
CssContext('editbox',
           parent = box,
           same_as_parent = True,
           tag='.edit-block',
           template='djpcms/style/box/editbox.css_t',
           data = {'padding':'2px',
                   'border': 'none'})

CssContext('hd',
           parent = box,
           tag='div.hd',
           template='djpcms/style/box/header.css_t',
           data={'padding':'6px 12px',
                 'text_transform':'uppercase',
                 'title_size':'110%',
                 'font_weight':'normal',
                 'overflow':'hidden'}),
CssContext('bd',
           parent = box,
           tag='div.bd',
           data={'padding':'5px 5px',
                 'border':'none'}),
CssContext('ft',
           parent = box,
           tag='div.ft',
           data={'padding':'5px 5px',
                 'overflow':'hidden',
                 'border':'none'})


#________________________________________ EDITING
CssContext('bodyedit',
           tag = 'body.edit',
           template='djpcms/style/editing.css_t',
           data = {
                   'background': '#f5f5f5',
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
                                     'padding':'5px 5px',
                                     'overflow':'hidden'}),
                    CssContext('bd',
                               tag='div.bd',
                               data={'padding':0})
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
           template='djpcms/style/search-box.css_t'
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
                   'padding':'4px 5px 4px 25px'}
           )


#________________________________________ ERROR LIST
CssContext('errorlist',
           tag='ul.messagelist li.error'
           )


#________________________________________ BREADCRUMBS
CssContext('breadcrumbs',
           tag = 'div.breadcrumbs',
           template = 'djpcms/style/breadcrumbs.css_t',
           data = {
                   'font_size': '130%',
                   'padding': '10px 0'}
           )
