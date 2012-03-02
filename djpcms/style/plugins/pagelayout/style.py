from medplate import CssContext, CssTheme, gradient, radius, shadow, variables

variables.declare('page_error_padding','10px')

variables.declare('footer_gradient',None)
variables.declare('footer_min_height','100px')
variables.declare('footer_font_size','90%')
variables.declare('footer_color',None)

CssContext('body-container',
           tag = '#body-container',
           data = {
              #'min-width': variables.body_min_width,
              'width': '100%',
              'overflow': 'hidden'
            })

CssContext('page-footer',
           tag = '#page-footer',
           data = {
            'gradient': variables.footer_gradient,
            'min-height': variables.footer_min_height,
            'font-size': variables.footer_font_size,
            'color': variables.footer_color,
            'overflow':'hidden'
            })

def head_body_footer(tiny_width = 400, tiny_top = 30):
    tw = '{0}px'.format(tiny_width)
    tt = '{0}px auto'.format(tiny_top)
            
    CssContext('body-container-tiny',
               tag = 'body.tiny',
               data = {
                'width': tw,
                'min-width': tw,
                'margin': tt
                })
    
    CssContext('body-container-tiny-page',
               tag = 'body.tiny #page-body',
               data = {
                'min-height': '0px'
            })
    
    CssContext('body-container-tiny-footer',
               tag = 'body.tiny #page-footer',
               data = {
                'min-height': '0px'
            })
               

head_body_footer()


CssContext('page-error',
           tag = '.page-error',
           data = {'padding': variables.page_error_padding}
           )

CssContext('content',tag='#content',
           data={'min_height':'500px',
                 'overflow':'hidden',
                 'padding':'0 0 20px 0',
                 'text_align':'left'})


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