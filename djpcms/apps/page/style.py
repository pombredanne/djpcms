from djpcms.media.style import *

def container_var(id, vars):
    vars.background = None
    vars.color = None
    vars.min_height = None
    vars.position = None
    vars.top = None
    vars.bottom = None
    vars.padding = None
    vars.width = pc(100)

    css(id,
        bcd(**vars.params()),
        width=vars.width,
        min_height=vars.min_height,
        position=vars.position,
        top=vars.top,
        bottom=vars.bottom,
        padding=vars.padding)  

################################################################################
##    CONTAINERS
container_var('#page-header', cssv.header)
container_var('#page-content', cssv.content)
container_var('#page-footer', cssv.footer)
