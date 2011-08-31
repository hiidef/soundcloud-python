SoundCloud-Python - SoundCloud API in Python
=========================================================

A wrapper for the [SoundCloud API](http://developers.soundcloud.com/docs/api/) written in Python.
This project is based on the [official SoundCloud package](http://github.com/soundcloud/python-api-wrapper) but uses OAuth 2.0 for authentication and provides some minor bug fixes.


Running tests
=============

The **SoundCloud API** comes with a small testsuite. It can be run automatically through either setuptools 
or nose.

Configuring tests
-----------------

Before you can run the tests, you need to configure them. You do this using the `test.ini` file in the
root of your working copy. Create a test app at http://soundcloud.com/you/apps/new and enter the appropriate credentials
in `test.ini`.

You will then need to obtain an access token for the tests to run with. Run

 python bootstrap_tests.py

and follow the instructions. Your browser bring you to the SoundCloud "connect" page. Connect with your app, and
your browser will be redirected to an URL with a query parameter called "code". Copy and paste this value to the
bootstrap_tests.py prompt, wait a moment, and check that the script finishes with a access_token=... line.
Copy and paste this line into your `test.ini` file.

Now you can run the tests!

Running tests through setuptools
--------------------------------

You can run the whole testsuite through setuptools_ by doing ::

  $ python setup.py test

Running tests through nose
--------------------------

If you want a more fine-grained control over which tests to run, you can use the `nosetests`-commandline tool.

Then to run individual tests, you can e.g. do::

  $ nosetests -s soundcloud.tests.soundcloud_tests:SoundcloudTests.test_setting_permissions


See the nose_-website for more options.



.. _nose: http://somethingaboutorange.com/mrl/projects/nose/
.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools
.. _ConfigObj: http://www.voidspace.org.uk/python/configobj.html


Creating the API-docs
=====================

Do::
   epydoc -v --name="SoundCloud API" --html -o docs/api soundcloud --exclude="os|mimetypes|urllib2|exceptions|mimetools"



