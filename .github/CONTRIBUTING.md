# How to contribute

Thank you for contributing Azely!
If you have some ideas to propose, please follow the contribution guide.
We use [GitHub flow][github-flow] for developing and managing the project.
The first section describes how to contribute with it.
The second and third sections explain how to prepare a local development environment and our automated workflows in GitHub Actions, respectively.


## Contributing with GitHub flow

### Create a branch

First of all, [create an issue][issues] with a simple title and get an issue ID (e.g., `#31`).
For example, if you propose to add functions for plotting something, the title of the issue would be `Add plotting feature`.
Using a simple verb (e.g., add, update, remove, fix, ...) in the present tense is preferable.

Then fork the repository to your account and create **a branch whose name begins with the issue ID** (e.g., `#31-plotting-feature` or simply `#31`).
We do not care about the naming of it (except for the issue ID) because the branch will be deleted after merging with the master branch.

### Add commits

After you update something, commit your change with **a message which starts with the issue ID**.
Using a simple verb in the present tense is preferable.

```shell
$ git commit -m "#31 Add plot functions"
```

Please make sure that your code (1) is formatted by [Black][black], (2) is checked by [Flake8][flake8] with the bundled config file (`.flake8`), and (3) passes the tests (`tests/test_*.py`) run by [pytest][pytest].
They are necessary to pass the status checks when you create a pull request.

If you add a new feature, please also make sure that you prepare tests for it.
For example, if you add the plotting module (`azely/plot.py`), write the series of test functions in `tests/test_plot.py`.

If you write a Python docstring, follow [the Google style][napoleon-google] so that it is automatically converted to a part of API docs by Sphinx.

### Open a Pull Request

When your code is ready, [create a pull request (PR)][pull-requests] to merge with the master branch.
Without special reasons, the title should be the same as that of the issue.
Please specify the issue ID in the comment form so that it is linked to the PR.
For example, writing `This PR closes #31.` at the beginning of the comment would be nice.

### Discuss and review your code

Your code is reviewed by at least one contributor and checked by the automatic status checks by [GitHub Actions][github-actions].
After passing them, your code will be merged with the master branch.
That's it!
Thank you for your contribution!

## Development environment

We manage the development environment (i.e., Python and its dependencies) with [Poetry][poetry].
After cloning the repository you forked, you can setup the environment by the following command.

```shell
$ poetry install
```

If you use [VS Code][vs-code] and [direnv][direnv], the following command will also setup the settings of VS Code for Python and an environment variable to specify the config directory of Azely (`AZELY_DIR`; see also README), respectively.

```shell
$ scripts/setup
```

Then the config directories (`.vscode` and `.azely`) will be created at the root of the repository (but ignored by `.gitignore`).


## GitHub Actions

### Testing, linting, and formatting

We have [a test workflow][test-workflow] for testing, linting, and formatting the code.
It is used for status checks when a pull request is created.
If you would like to check them in local, the following commands are almost equivalent (the difference is the workflow is run under multiple Python versions).

```shell
$ poetry run pytest
$ poetry run flake8 docs tests azely
$ poetry run black --check docs tests azely
```

### Publish to PyPI

We have [a PyPI workflow][pypi-workflow] for publishing the package to [PyPI][pypi].
When [a release is created][release], the workflow is triggered and the package is automatically built and uploaded to PyPI.

### Deploy docs

We have [a GitHub Pages workflow][gh-pages-workflow] for publishing the HTML docs.
When [a release is created][release], the workflow is triggered and the docs are automatically built and deployed to [the gh-pages branch][gh-pages-branch].


[black]: https://black.readthedocs.io/en/stable/
[direnv]: https://direnv.net/
[flake8]: https://flake8.pycqa.org/en/latest/
[gh-pages-workflow]: https://github.com/astropenguin/azely/blob/master/.github/workflows/gh-pages.yml
[gh-pages-branch]: https://github.com/astropenguin/azely/tree/gh-pages
[github-actions]: https://github.com/astropenguin/azely/actions
[github-flow]: https://guides.github.com/introduction/flow/
[issues]: https://github.com/astropenguin/azely/issues?q=is%3Aissue
[napoleon-google]: https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google
[poetry]: https://python-poetry.org/
[pull-requests]: https://github.com/astropenguin/azely/pulls?q=is%3Apr
[pypi]: https://pypi.org/project/azely/
[pypi-workflow]: https://github.com/astropenguin/azely/blob/master/.github/workflows/pypi.yml
[pytest]: https://docs.pytest.org/en/stable/
[release]: https://github.com/astropenguin/azely/releases
[test-workflow]: https://github.com/astropenguin/azely/blob/master/.github/workflows/test.yml
[vs-code]: https://code.visualstudio.com/
