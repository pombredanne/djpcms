from medplate import CssContext, CssTheme

context_menu = CssContext('context-menu',
                          tag = '#contextmenu',
                          template = 'djpkit/context-menu.css_t',
                          data = {
                                  'line_height': '18px',
                                  'position': 'absolute',
                                  'z_index': 99997,
                                  'min_width': '120px',
                                  'font_size': '1em',
                                  'anchor_padding': '4px 0',
                                  }
                          )


floating_input = CssContext('floating-input',
                            tag = '#floating-input',
                            template = 'djpkit/floating-input.css_t',
                            data = {}
                            )

CssContext('vsplitbar',
           tag = '.vsplitbar',
           data = {
                'height':'100%'
        }
)
CssContext('hsplitbar',
           tag = '.hsplitbar',
           data = {
                'width':'100%'
        }
)

CssTheme(context_menu,
         'smooth',
         data = {
                 'background':'#ccc',
                 'shadow': '4px 4px 2px rgba(0,0,0, .3)'
                 }
         )


CssTheme(floating_input,
         'smooth',
         data = {
                 'border':'1px solid #ccc',
                 }
         )