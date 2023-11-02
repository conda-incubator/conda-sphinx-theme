import os
import time
import datetime
# Configuration file for the Sphinx documentation builder for
# conda projects.

# Release mode enables optimizations and other related options.
is_release_build = tags.has('release')  # noqa

# Parse year using SOURCE_DATE_EPOCH, falling back to current time.
# https://reproducible-builds.org/specs/source-date-epoch/
build_date = datetime.datetime.utcfromtimestamp(
    int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
)

# -- Project information -----------------------------------------------------

project = "Conda Sphinx Theme"
copyright = (
    f"2023 conda-incubator"
)
author = "conda-incubator"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_favicon",
]

# Add any paths that contain templates here, relative to this directory.

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "conda_sphinx_theme"
html_theme_options = {
    "logo": {
        "text": "conda sphinx theme"
    },
    # logo is installed by mpl-sphinx-theme as:
    # "logo": {"link": "https://matplotlib.org/stable/",
    #         "image_light": "_static/logo_light.svg",
    #         "image_dark": "_static/logo_dark.svg"},
    # if this default is OK, then no need to modify "logo"
    # collapse_navigation in pydata-sphinx-theme is slow, so skipped for local
    # and CI builds https://github.com/pydata/pydata-sphinx-theme/pull/386
    "collapse_navigation": not is_release_build,
    "show_prev_next": False,
    # Determines the type of links produced in the navigation header:
    # - absolute: Links point to the URL https://matplotlib.org/...
    # - server-stable: Links point to top-level of the server /stable/...
    # - internal: Links point to the internal files as expanded by the `pathto`
    #   template function in Sphinx.
    "navbar_links": "absolute",

    # Navbar icon links
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/conda-incubator/conda-sphinx-theme",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
        {
            "name": "Element",
            "url": "http://bit.ly/conda-chat-room",
            "icon": "_static/element_logo.svg",
            "type": "local",
        },
        {
            "name": "Discourse",
            "url": "https://conda.discourse.group/",
            "icon": "fa-brands fa-discourse",
            "type": "fontawesome",
        },
    ],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]
