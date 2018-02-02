from setuptools import setup

setup(name = 'azely',
      description = 'Calculate azimuth/elevation of astronomical objects',
      version = '0.2',
      author = 'snoopython',
      author_email = 'taniguchi@ioa.s.u-tokyo.ac.jp',
      url = 'https://github.com/snoopython/azely',
      keywords = 'astronomy visualization python azimuth elevation',
      packages = ['azely'],
      package_data = {'azely': ['data/*.yaml']},
      entry_points = {'console_scripts': ['azely=azely.cli:main']},
      install_requires = ['astropy', 'numpy', 'pyyaml'])
