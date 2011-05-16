from medplate import CssContext


mtree = CssContext('mtree',
                   tag = '.mtree',
                   template = 'jquery_mtree/mtree.css_t',
                   data = {
                           'text_align':'left',
                           'overflow': 'hidden',
                           'background': '#fff',
                           'padding': '10px 0',
                           'icon_size': '18px',
                           #
                           #'hovered_background': '#e7f4f9',
                           #'hovered_border':'1px solid #e7f4f9'
                           #
                           #'clicked_background': 'navy',
                           #'clicked_color':'white'
                           }
                   )


CssContext('tableview',
           tag = '.tableview',
           template = 'jquery_mtree/table.css_t',
           parent = mtree,
           same_as_parent = True,
           data = {
                   'padding': '0',
                   'summary_background_color': '#e6e6e6',
                   'splitter_color': '#aaa',
                   'border': '1px solid #aaa'
                   }
           )
