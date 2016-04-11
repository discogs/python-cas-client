#!/usr/bin/env python
import setuptools


with open('README.rst', 'r') as file_pointer:
    long_description = file_pointer.read()

with open('cas_client/_version.py', 'r') as file_pointer:
    exec(file_pointer.read())


setuptools.setup(
    author='Josiah Wolf Oberholtzer',
    author_email='joberholtzer@discogsinc.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration :: Authentication/Directory',
        ],
    description='A Python CAS client',
    include_package_data=True,
    install_requires=[
        'PyCrypto',
        'requests',
        'six',
        'tox',
        ],
    keywords=[
        'auth',
        'authentication',
        'cas',
        'cas2',
        'cas3',
        'client',
        'single sign-on',
        'sso',
        ],
    license='MIT',
    long_description=long_description,
    name='cas_client',
    packages=['cas_client'],
    platforms='any',
    url='https://github.com/discogs/python-cas-client',
    version=__version__,
    )
