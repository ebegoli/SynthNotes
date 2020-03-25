#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

requirements = [
    "tqdm",    
    "numpy",
    "pandas",
    "lxml",
    "pyarrow",
    "fastparquet",
    "stringdist",
    "scikit-learn",
    "scipy",

]

#    "python-snappy",

setup(
    name='synthnotes',
    version='0.2.0',
    description="A generator of synthetic clinical notes",
    # long_description=readme + '\n\n' + history,
    author="Edmon Begoli",
    author_email='begolie@ornl.gov',
    # url='https://github.com/ebegoli/SynthNotes',
    packages=find_packages(exclude=['synthnotes.resources']),
    include_package_data=True,      # Tells setuptools to include all files in the MANIFEST
    package_data={
            'synthnotes.resources': ['*.json', "*.template", "*.csv"],
      },
    zip_safe=False,
    install_requires=requirements,
    license="MIT license",
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
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'synthnotes = synthnotes.__main__:cli'
        ]
    }
)
