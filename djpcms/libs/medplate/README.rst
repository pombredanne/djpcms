===================
Medplate
===================

A djpcms_ library for creating ``css`` files from templates and
a compressor for both ``css`` and ``javascript`` files.
These are two distinct tasks with no dependency with one onother, they have
been assembled in one package since they both operate on static files.


Creating css files
==========================

* Add a ``style`` python module within your site directory and
  add at least the following context::

	from medplate import CssContext
	
	CssBody()
	
  or with some information::
    
    from medplate import CssContext
    
    root = CssBody(data = {
                           'font_size': '13px',
                           'line_height': '18px',
                           'font_family': "'Lucida Grande',Arial,sans-serif",
                           'block_spacing': '15px'
                           }
    )
    
    CssContext('anchor',
               data = {'color':'#36566B',
                       'color_hover':'#e17009',
                       'font_weight':'bold'
                       }
               )
	

* Add a ``body.css_t`` file within your site templates directory and add::

    {% extends "medplate/body.css_t" %}

    {% block body %}
    ..... your stuff here
    {% endblock %}
    

Run::

	python manage.py style -s <yourstylename>
	

Compress
==============


.. _djpcms: www.djpcms.com

