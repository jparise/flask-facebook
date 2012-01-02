#!/usr/bin/env python

from setuptools import setup

version = __import__('flask_facebook').__version__

setup(
    name='Flask-Facebook',
    version=version,
    url='http://github.com/jparise/flask-facebook',
    license='BSD',
    author='Jon Parise',
    author_email='jon@indelible.org',
    description='Adds Facebook support to your Flask application',
    long_description=__doc__,
    packages=['flask_facebook'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'setuptools',
        'Flask',
        'facebook-sdk'
    ],
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
