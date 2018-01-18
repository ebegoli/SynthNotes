#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "tqdm",
    "faker",
]

setup_requirements = [
    # TODO(sudarshan85): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='synthnotes',
    version='0.1.0',
    description="A generator of synthetic psychiatric notes",
    long_description=readme + '\n\n' + history,
    author="Edmon Begoli",
    author_email='begolie@ornl.gov',
    url='https://github.com/ebegoli/SynthNotes',
    packages=find_packages(include=['synthnotes']),
    include_package_data=True,      # Tells setuptools to include all files in the MANIFEST
    package_data={
            'synthnotes.resources': ['*.json', "*.template"],
      },
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='synthnotes',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
