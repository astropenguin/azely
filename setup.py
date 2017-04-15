# coding: utf-8

"""Python 3 tool to plot azimuth and elevation of astronomical objects"""

# standard library
from setuptools import setup

# dependent packages
import azely


# functions
setup(
    name = 'azely',
    description = __doc__,
    version = azely.__version__,
    author = azely.__author__,
    license = azely.__license__,
    author_email = 'taniguchi@ioa.s.u-tokyo.ac.jp',
    url = 'https://github.com/snoopython/azely',
    keywords = 'astronomy visualization python',
    packages = ['azely'],
    package_data = {'azely': ['data/*.yaml']},
    entry_points = {'console_scripts': ['azely=azely.main:main']},
    install_requires = ['docopt', 'pyephem', 'pyyaml'],
)
