from djpcms.style import CssContext, object_definition

CssContext('redisserver',
           tag = 'div.object-definition.redisserver',
           template='djpcms/style/object-definition.css_t',
           process = object_definition,
           data = {
            'left_width':50
            }
)

