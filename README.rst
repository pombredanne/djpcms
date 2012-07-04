:Web: http://djpcms.com/
:Documentation: http://djpcms.com/docs/
:Dowloads: http://pypi.python.org/pypi/djpcms/
:Source: http://github.com/lsbardel/djpcms
:Keywords: web, cms, dynamic, ajax, python, jquery

--

Djpcms is a dynamic Content Management System which uses Python on the server side
and Javascript with jQuery_ on the browser side.
It is designed to handle dynamic applications which require
high level of customization.
Lots of AJAX enabled features including inline editing, autocomplete,
ajax forms, dynamic tables and more.
It works with Python_ 2.6 and up including python 3 series.
Djpcms does not use any template language, it uses Python alone to render on the
server side.


.. contents::
    :local:

.. _intro-features:

Features
===============================

* Dynamic pages based on database models.
* Applications based on database model or not.
* Extendible using ``plugins``.
* Inline editing of ``plugins`` and ``pages``.
* Move ``plugins`` in page using drag-and-drop functionalities.
* Font icons from Fontawesome_.
* ``Autocomplete`` for models.
* DataTables_ integration.
* Extendible AJAX decorators.
* Tagging included in distribution.
* Several battery included application classes.
* Nice form layout with extendible ``uniforms``.
* Sitemap design.


.. _intro-installing:

Installing
================================
You can download the latest archive from pypi_, uncompress and::

	python setup.py install
	
Otherwise you can use pip::

	pip install djpcms
	
or easy_install::

	easy_install djpcms
	
	
Version Check
=====================

To check the version::

	>>> import djpcms
	>>> djpcms.__version__
	'0.9.0'
	>>> djpcms.get_version()
	'0.9.0'
	
	
Running tests
===================

On the top level directory type::

	python runtests.py
	
For options in running tests type::

    python runtests.py --help
    
Tests can also be run for specific tags, For a list of tags type::

    python runtests.py --list
	
To access coverage of tests you need to install the coverage_ package and run the tests using::

	coverage run runtests.py
	
and to check out the coverage report::

	coverage report -m
	
Optional requirements
========================
The core library requires Python_ 2.6 or above, nothing else
(the jinja2_ template engine is shipped with the distribution).
Optional (recommended) requirements are

* stdnet_ for Redis object relational mapping.
* sqlalchemy_ for relational databases.


Kudos
=====================
Djpcms includes several open-source libraries and plugins developed
by other authors and communities:

Python
---------
* django_ for ideas and code snippets.

.. _jquery-plugins:

JavaScript
------------
* jQuery_ core and UI are the building block of the browser side of djpcms.
* jQuery form_ plugin for AJAX forms.
* jQuery DataTables_ plugin for managing dynamic tables. 
* jQuery cycle_ plugin for photo galleries. 
* jQuery bsmSelect_ plugin for multiple select.
* Modernizr_, a small JavaScript library that detects the availability o
  native implementations for next-generation web technologies.
* Fontawesome_ for font icons (`djpcms.style.plugins.fontawesome`).


.. _pypi: http://pypi.python.org/pypi?:action=display&name=djpcms
.. _Python: http://www.python.org/
.. _jinja2: http://jinja.pocoo.org/docs/
.. _django: http://www.djangoproject.com/
.. _jQuery: http://jquery.com/
.. _fabric: http://docs.fabfile.org/
.. _pip: http://pip.openplans.org/
.. _South: http://south.aeracode.org/
.. _stdnet: http://lsbardel.github.com/python-stdnet/
.. _Modernizr: http://www.modernizr.com/
.. _cycle: http://jquery.malsup.com/cycle/
.. _bsmSelect: https://github.com/vicb/bsmSelect
.. _coverage: http://nedbatchelder.com/code/coverage/
.. _DataTables: http://www.datatables.net/
.. _form: http://jquery.malsup.com/form/
.. _Fontawesome: http://fortawesome.github.com/Font-Awesome/