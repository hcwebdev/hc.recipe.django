This recipe when used will do the following:

 * install ``Django`` and all its dependecies.

 * generates the management and test scripts in the bin directory

Supported options
=================

The recipe supports the following options:

eggs
    Eggs you want the recipe to install.  Django is added automatically
    if it is not provided.

project
    The name of the django project to build the scripts against.

settings
    The dot-notation name of the django settings file to use by default.  Omit the
    project name from the beginning. ie. development - not project.development
    
    Defaults to ``settings``

manage-script
    The (optional) management script you want build.
    
    The value of ``manage-script`` will be the name of a generated Django manage.py
    script which loads the settings file specified.

test-script
    The name to give to the generated testrunner script.  Ignored unless ``test``
    is provided.  If omitted and ``test`` is provided, it will be titled ``runtests``.

test-settings
    The dot-notation name of a django settings file to use for running tests.  Omit 
    the project name from the beginning. ie. development - not project.development
    
    If omitted, it will be set to the value for ``settings``.

test
    An optional list of applications to run the testrunner against.  No testrunner will be 
    generated if this list is omitted.

wsgi
    An extra script is generated in the bin folder when this is set to ``true``. 
    This can be used with mod_wsgi to deploy the project. The name of the script 
    is ``PART_NAME``.wsgi.

wsgi-file-name
    Provide an alternate name for the wsgi script.  Will append ``.wsgi`` if it doesn't
    end with it.

wsgilog
    In case the WSGI server you're using does not allow printing to stdout, you can 
    set this variable to a filesystem path - all stdout/stderr data is redirected 
    to the log instead of printed.



Example usage
=============

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = django
    ... index = http://pypi.python.org/simple
    ...
    ... [django]
    ... recipe = hc.recipe.django
    ... project = project
    ... manage-script = manage_development
    ... settings = development
    ... test-script = run_project_tests
    ... test-settings = testing
    ... test =
    ...       app1
    ...       app2
    ... """)

Running the buildout gives us::

    >>> print system(buildout)
    Getting distribution for 'zc.recipe.egg'.
    ...
    Installing django.
    Getting distribution for 'Django'.
    ...
    Got Django...
    Generated script '/sample-buildout/bin/manage_development'.
    Generated script '/sample-buildout/bin/run_project_tests'.
    <BLANKLINE>

Check that we have the management and testrunner scripts::

    >>> ls(sample_buildout, 'bin')
    -  buildout
    -  manage_development
    -  run_project_tests

You can now just run the management script like this::

    $ bin/manage_development <COMMAND>

And run the project's tests with::

    $ bin/run_project_tests

If we look at the generated management script we will see that the 
propert settings file is given as argument::

    >>> cat('bin', 'manage_development') #doctest: +REPORT_NDIFF
    ...
    <BLANKLINE>
    ...
    <BLANKLINE>
    import hc.recipe.django.commands.manage
    <BLANKLINE>
    if __name__ == '__main__':
        hc.recipe.django.commands.manage.main('project.development')

The generated testing script is provided the specified settings file
and Django apps which are to be tested::

    >>> cat('bin', 'run_project_tests') #doctest: +REPORT_NDIFF
    ...
    <BLANKLINE>
    ...
    <BLANKLINE>
    import hc.recipe.django.commands.test
    <BLANKLINE>
    if __name__ == '__main__':
        hc.recipe.django.commands.test.main('project.testing', 'app1', 'app2')


We'll adjust the buildout to generate a wsgi script::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = django
    ... index = http://pypi.python.org/simple
    ...
    ... [django]
    ... recipe = hc.recipe.django
    ... project = project
    ... manage-script = manage_development
    ... settings = development
    ... test-script = run_project_tests
    ... test-settings = testing
    ... test =
    ...       app1
    ...       app2
    ... wsgi = true
    ... """)


Running the buildout gives us::

    >>> print system(buildout)
    Uninstalling django.
    Installing django.
    ...
    Generated script '/sample-buildout/bin/django.wsgi'.
    <BLANKLINE>


We'll adjust the buildout to set the wsgi script name::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = django
    ... index = http://pypi.python.org/simple
    ...
    ... [django]
    ... recipe = hc.recipe.django
    ... project = project
    ... manage-script = manage_development
    ... settings = development
    ... test-script = run_project_tests
    ... test-settings = testing
    ... test =
    ...       app1
    ...       app2
    ... wsgi = true
    ... wsgi-file-name = development
    ... """)


Running the buildout gives us::

    >>> print system(buildout)
    Uninstalling django.
    Installing django.
    ...
    Generated script '/sample-buildout/bin/development.wsgi'.
    <BLANKLINE>



