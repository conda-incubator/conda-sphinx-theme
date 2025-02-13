import os
import time
import datetime
from importlib.metadata import version as get_version
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

release: str = get_version("conda_sphinx_theme")
# for example take major/minor
version: str = ".".join(release.split('.')[:2])

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
    "show_prev_next": False,
    "github_url": "https://github.com/conda-incubator/conda-sphinx-theme",
    "goatcounter_url": "",  # Disabled by default; put your own GoatCounter URL here to enable
    "icon_links": [
        {
            "name": "Element",
            "url": "https://matrix.to/#/#conda:matrix.org",
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

html_context = {
    "goatcounter_dashboard_url": ""  # Link to your GoatCounter dashboard
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

source_suffix = ".rst"

# The master toctree document.
master_doc = "index"
