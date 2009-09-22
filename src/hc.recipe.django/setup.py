# -*- coding: utf-8 -*-
"""
This module contains the tool of hc.recipe.django
"""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'hc.recipe.django'
version = '0.3.5'
long_description = '\n'.join([
    read('docs', 'README.txt'),
    'Changelog',
    '*********',
    '',
    read('docs', 'CHANGES.txt'),
    'Detailed Documentation',
    '**********************',
    '',
    read('hc', 'recipe', 'django', 'README.txt'),
])
tests_require = ['zope.testing']


setup( 
    name=name,
    version=version,
    description="A buildout recipe to install django and manage a django project",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        'Framework :: Buildout',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='buildout recipe django',
    author='Jacob Radford',
    author_email='webmaster@hunter.cuny.edu',
    url='http://pypi.python.org/pypi/hc.recipe.django',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['hc', 'hc.recipe'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.egg',
        # -*- Extra requirements: -*-
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),
    test_suite = '%s.tests.test_suite' % name,
    entry_points= {
        'zc.buildout': ['default = %s:Recipe' % name]
    },
)
