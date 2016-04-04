#!/usr/bin/env python
import setuptools


install_requires = [
    'PyCrypto',
    'requests',
    'six',
    'tox',
    ]


if __name__ == '__main__':
    setuptools.setup(
        include_package_data=True,
        install_requires=install_requires,
        name='cas_client',
        packages=['cas_client'],
        )
