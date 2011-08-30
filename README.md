SoundCloud-Python - Implements SoundCloud's API in Python
=========================================================

A wrapper for the [SoundCloud API](http://developers.soundcloud.com/docs/api/) written in Python.
This project is based on the [official SoundCloud package](http://github.com/soundcloud/python-api-wrapper) but uses OAuth 2.0 for authentication and provides some minor bug fixes.


Running tests
=============

The **SCAPI** comes with a small testsuite. It can be run automatically through either setuptools_ 
or nose_.

Configuring tests
-----------------

Before you can run the tests, you need to configure them. You do this using the `test.ini` file in the
root of python **SCAPI** workingcopy.

Running tests through setuptools
--------------------------------

You can run the whole testsuite through setuptools_ by doing ::

  host:~/SoundCloudAPI deets$ python setup.py test

Running tests through nose
--------------------------

If you want a more fine-grained control over which tests to run, you can use the `nosetests`-commandline tool.

Then to run individual tests, you can e.g. do::

  host:~/SoundCloudAPI deets$ nosetests -s scapi.tests.scapi_tests:SCAPITests.test_setting_permissions


See the nose_-website for more options.



.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _ConfigObj: http://www.voidspace.org.uk/python/configobj.html


Creating the API-docs
=====================

Do::
   epydoc -v --name="SoundCloud API" --html -o docs/api scapi --exclude="os|mimetypes|urllib2|exceptions|mimetools"



