# Project information
project = "Azely"
copyright = "2017-2020, Akio Taniguchi"
author = "Akio Taniguchi"
release = "0.5.2"


# General configuration
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# Options for HTML output
html_static_path = ["_static"]
html_logo = "_static/logo.svg"
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "github_url": "https://github.com/astropenguin/azely/",
    "twitter_url": "https://twitter.com/astropengu_in/",
}
