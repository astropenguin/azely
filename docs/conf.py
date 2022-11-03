# Project information
project = "Azely"
copyright = "2017-2020, Akio Taniguchi"
author = "Akio Taniguchi"
release = "0.6.0"


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
# project information
author = "Akio Taniguchi"
copyright = "2017-2022, Akio Taniguchi"


# general configuration
add_module_names = False
autodoc_typehints = "both"
autodoc_typehints_format = "short"
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
myst_heading_anchors = 3
templates_path = ["_templates"]


# options for HTML output
html_static_path = ["_static"]
html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "logo": {
        "image_light": "logo-light.svg",
        "image_dark": "logo-dark.svg",
    },
    "github_url": "https://github.com/astropenguin/pandas-dataclasses/",
    "twitter_url": "https://twitter.com/astropengu_in/",
}
