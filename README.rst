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
Lots of AJAX enabled features including inline editing, autocomplete and
ajax forms.
It works with Python_ 2.6 and up including python 3 series.
The template engine is jinja2_ which is shipped with the distribution.


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
  It is required by ``djpcms.contrib.monitor`` and ``djpcms.contrib.sessions`` modules.
* fabric_ and pip_ for the ``djpcms.contrib.jdep`` module.


Kudos
=====================
Djpcms includes several open-source libraries and plugins developed
by other authors and communities:

Python
---------
* jinja2_ for templating. Shipped with the library in the ``libs``
  module but a library in its own.

JavaScript
------------
* jQuery_ core and UI are the building block of the browser side of djpcms. 
* jQuery tablesorter_ plugin for managing dynamic tables.
* jQuery jstree_ plugin for managing tree components. 
* jQuery cycle_ plugin for photo galleries. 
* jQuery Sparklines_ plugin for inline plotting.
* Modernizr_, a small JavaScript library that detects the availability of native implementations for next-generation web technologies.

In addition, several ideas and code snippets have been taken from django_.


.. _pypi: http://pypi.python.org/pypi?:action=display&name=djpcms
.. _Python: http://www.python.org/
.. _jinja2: http://jinja.pocoo.org/docs/
.. _django: http://www.djangoproject.com/
.. _jQuery: http://jquery.com/
.. _fabric: http://docs.fabfile.org/
.. _pip: http://pip.openplans.org/
.. _South: http://south.aeracode.org/
.. _stdnet: http://lsbardel.github.com/python-stdnet/
.. _tablesorter: http://tablesorter.com/
.. _Modernizr: http://www.modernizr.com/
.. _jstree: http://www.jstree.com/
.. _cycle: http://jquery.malsup.com/cycle/
.. _Sparklines: http://www.omnipotent.net/jquery.sparkline/
.. _coverage: http://nedbatchelder.com/code/coverage/
.. _DataTables: http://www.datatables.net/