:Web: http://djpcms.com/
:Documentation: http://djpcms.com/docs/
:Dowloads: http://pypi.python.org/pypi/djpcms/
:Source: http://github.com/lsbardel/djpcms
:Keywords: web, cms, dynamic, ajax, python, jquery

--

Djpcms is a dynamic Content Management System which uses Python on the server side
and Javascript with jQuery_ on the browser side.
It is designed to handle dynamic applications requiring
high level of customization.
Lots of AJAX enabled features including inline editing, autocomplete,
ajax forms, dynamic tables and more.
It works with Python_ 2.6 and up including python 3 series.
Djpcms does not use any template specific language, it uses Python alone
to render on the server side.


.. contents::
    :local:

.. _intro-features:

Features
===============================

* Dynamic pages based on database models or not.
* Applications based on database model or not.
* Extendible using ``plugins``.
* Inline editing of ``plugins`` and ``pages``.
* Move ``plugins`` in page using drag-and-drop functionalities.
* Font icons from Fontawesome_.
* ``Autocomplete`` functionality.
* DataTables_ integration.
* Extendible AJAX decorators.
* Several battery included application classes.
* Extendible form layouts.
* Sitemap design.


.. _intro-installing:

Installing
================================
You can download the latest archive from pypi_, uncompress and::

	python setup.py install
	
Otherwise you can use pip::

	pip install djpcms
	
	
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
The core library requires pulsar_. Optional (recommended) requirements are

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
* jQuery_ core and UI are the building block.
* jQuery form_ plugin for AJAX forms.
* jQuery DataTables_ plugin for managing dynamic tables.
* Fontawesome_ for font icons (`djpcms.style.plugins.fontawesome`).


.. _pypi: http://pypi.python.org/pypi?:action=display&name=djpcms
.. _Python: http://www.python.org/
.. _pulsar: https://github.com/quantmind/pulsar
.. _django: http://www.djangoproject.com/
.. _jQuery: http://jquery.com/
.. _pip: http://pip.openplans.org/
.. _stdnet: http://lsbardel.github.com/python-stdnet/
.. _cycle: http://jquery.malsup.com/cycle/
.. _coverage: http://nedbatchelder.com/code/coverage/
.. _DataTables: http://www.datatables.net/
.. _form: http://jquery.malsup.com/form/
.. _Fontawesome: http://fortawesome.github.com/Font-Awesome/