from djpcms.contrib.medplate.defaults import template, base_context

context = base_context.copy()

context.update({ 
    'color': '#333',
    'edit_background': '#f5f5f5'})