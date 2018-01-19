"""Python 3 tool to plot azimuth and elevation of astronomical objects"""

# standard library
from setuptools import setup


# functions
setup(
    name = 'azely',
    description = __doc__,
    version = '0.2',
    author = 'snoopython',
    author_email = 'taniguchi@ioa.s.u-tokyo.ac.jp',
    url = 'https://github.com/snoopython/azely',
    keywords = 'astronomy visualization python',
    packages = ['azely'],
    package_data = {'azely': ['data/*.yaml']},
    entry_points = {'console_scripts': ['azely=azely.cli:main']},
    install_requires = ['docopt', 'pyephem', 'pyyaml'],
)
