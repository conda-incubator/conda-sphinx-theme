from __future__ import annotations

from datetime import datetime, timezone
import os
import time
from importlib.metadata import version as get_version
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Final

# Configuration file for the Sphinx documentation builder for
# conda projects.

# Release mode enables optimizations and other related options.
is_release_build: Final = tags.has('release')  # noqa

# Parse year using SOURCE_DATE_EPOCH, falling back to current time.
# https://reproducible-builds.org/specs/source-date-epoch/
timestamp: Final = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
build_date: Final = datetime.fromtimestamp(timestamp, timezone.utc)

# -- Project information -----------------------------------------------------

project: Final = "Conda Sphinx Theme"
copyright: Final = "2023 conda-incubator"
author: Final = "Anaconda, Inc."

release: Final = get_version("conda_sphinx_theme")
# for example take major/minor
version: Final = ".".join(release.split('.')[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions: Final = [
    "sphinx_favicon",
]

# Add any paths that contain templates here, relative to this directory.

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: Final = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme: Final = "conda_sphinx_theme"
html_theme_options: Final = {
    "show_prev_next": False,
    "github_url": "https://github.com/conda-incubator/conda-sphinx-theme",
    "goatcounter_url": None,  # Disabled by default; put your own GoatCounter URL here to enable
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

source_suffix: Final = ".rst"

# The master toctree document.
master_doc: Final = "index"
