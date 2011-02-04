from djpcms.contrib.medplate.themes.allwhite import base_context


context = base_context.copy()


context.update({
    'color': '#333',
    'edit_background': '#f5f5f5',
    # BOX
    'box': {'hd': {'background':'transparent'},
            'bd': {'background':'transparent'},
            'ft': {'background':'transparent'}},
    })


# Uniforms
context.uniform.update({'input_border':'2px solid #dfdfdf'})