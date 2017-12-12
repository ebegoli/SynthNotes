from setuptools import setup, find_packages

""" TODO: 
I'm certain this needs to be filled out more and have more fields added to setup.
I'm not familiar with those so I added the bare bones info for now.
Seems we need to include:
    entry_points:console_scripts
    
Also need to decide on how we will do version schemes.  

For reference I was working on the Python packaging user guide:
https://media.readthedocs.org/pdf/python-packaging-user-guide/latest/python-packaging-user-guide.pdf
"""
setup(name="SynthNotes",
      version="0.0.1",
      description="A package for generating synthetic psychiatric SOAP notes.",
      url="https://github.com/ebegoli/SynthNotes",
      author="UTK, ORNL",
      license="MIT",
      python_requires=">=3",
      keywords="SOAP synthetic psychiatric notes",
      install_requires=[
          "tqdm",
          "faker",
      ],
      packages=find_packages()
      )
