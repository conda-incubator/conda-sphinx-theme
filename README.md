# Conda Sphinx Theme

This is the Conda Sphinx Theme. It extends the [PyData Sphinx Theme][pydata-sphinx-theme]
project  by adding custom styling.

## Install

You can install the `conda-sphinx-theme` via conda-forge:

```
conda install -c conda-forge conda-sphinx-theme
```

or PyPI:

```
pip install conda-sphinx-theme
```

## Configuring

When creating a conda subproject you can include this theme by changing this
line in your conf.py file

```python
html_theme = 'conda_sphinx_theme'
```

## Navigation

The navbar links to the other documentation sites in the conda ecosystem, and the
theme ships the list. The site being viewed leads the navbar, every other entry
folds into a dropdown menu, and `conda.org` always shows at the end.

The list lives in
[`conda_sphinx_theme/projects.json`](conda_sphinx_theme/projects.json). To add or
reorder a site, edit that file:

```json
[
  {
    "name": "conda",
    "docs": "https://docs.conda.io/projects/conda/en/stable/",
    "github": "https://github.com/conda/conda",
    "package": "conda",
    "channels": ["main", "conda-forge"]
  }
]
```

| Field | Required | Purpose |
|---|---|---|
| `name` | yes | Navbar label, also matches the Sphinx `project` value |
| `docs` | yes | Documentation URL |
| `github` | no | Source link on the projects page |
| `package` | no | anaconda.org package name, defaults to `name`; only needed when they differ |
| `channels` | no | Version badge channels, defaults to `["main", "conda-forge"]`; `[]` shows no badges, and channels a package is not published to render as "not found" |

The site being viewed always leads the links: an entry whose name matches the
Sphinx `project` value - with spaces and underscores read as dashes, so
`Conda Sphinx Theme` matches `conda-sphinx-theme` - renders first as the current
tab and links to the docs root, keeping versioned and local builds on-site. It is
not repeated in the menu. A project with no matching entry gets a tab of its own
under its `project` name.

The navbar and the projects page are rendered from this list at build time, so an
edit shows up on the next build, and immediately under `pixi run docs-live`
(which watches the theme package). Consuming projects pick the list up with the
theme version they pin.

Long lists stay usable: the menu scrolls, and once JavaScript runs it also gets
a filter box above the entries ("All projects" stays visible). Without
JavaScript the filter is hidden and the plain list remains.

The theme also generates a `/projects` page listing every entry in a table, with
documentation and source links plus version badges for each configured channel,
sorted alphabetically. Each badge is labelled with its channel name and links to
the corresponding anaconda.org page. Set `projects_page = false` in `html_theme_options` to
skip it, and set `projects` there to use a different list for one project.

## Version Anchors Extension

The theme includes a `version_anchors` Sphinx extension that automatically creates anchors for version headings in changelog files. This makes it easy to link directly to specific versions in your changelog.

### Usage

To use the version anchors extension, add it to your `extensions` list in `conf.py`:

```python
extensions = [
    # ... your other extensions
    "conda_sphinx_theme.version_anchors",
]
```

### How it works

The extension automatically detects changelog files (files with names containing "changelog", "release", "history", or "news") and scans for headings that match version patterns. When found, it creates anchor IDs that you can link to.

For example, if you have a heading like:

```
25.5.0 (2025-05-21)
===================
```

The extension will create an anchor with ID `version-25.5.0` that you can link to with `:version:`25.5.0`` (recommended), `:ref:`version-25.5.0``, or by URL fragment `#version-25.5.0`.

### Configuration

You can customize the behavior with these configuration options in your `conf.py`:

```python
# Pattern to match version headings (must have exactly one capture group for the version)
version_anchor_pattern = r"^(\d+\.\d+(?:\.\d+)?)\s*\(.*?\)$"  # Default

# Format template for anchor IDs (use {version} as placeholder)
version_anchor_format = "version-{version}"  # Default (REQUIRED: must contain {version})

# File patterns that indicate changelog files (case-insensitive)
version_anchor_changelog_files = ["changelog", "release", "history", "news"]  # Default
```

**Note**: The `version_anchor_format` must contain the `{version}` placeholder. The extension will validate this at startup and raise an error if the placeholder is missing.

Alternative patterns and formats you might want to use:

```python
# For "Version 1.2.3" format
version_anchor_pattern = r"^Version\s+(\d+\.\d+(?:\.\d+)?).*$"

# For "Release 1.2.3" format
version_anchor_pattern = r"^Release\s+(\d+\.\d+(?:\.\d+)?)"

# For "v1.2.3" or "1.2.3" format
version_anchor_pattern = r"^v?(\d+\.\d+(?:\.\d+)?)"

# Alternative anchor formats:
version_anchor_format = "v{version}"           # Creates anchors like "v25.5.0"
version_anchor_format = "release-{version}"    # Creates anchors like "release-25.5.0"
version_anchor_format = "{version}"            # Creates anchors like "25.5.0" (not recommended for HTML4/XHTML)
```

## Development

This project uses [pixi](https://pixi.sh) for development and dependency management.

### Setup

```bash
# Install pixi (if not already installed)
curl -fsSL https://pixi.sh/install.sh | bash

# Install all environments
pixi install --all
```

### Available Commands

**Testing:**

```bash
pixi run test          # Run tests with coverage
pixi run test-fast     # Run tests without coverage
pixi run ci            # Run full CI pipeline (lint + type-check + test)
```

**Documentation:**

```bash
pixi run docs-build    # Build documentation
pixi run docs-live     # Build docs with live reload (opens browser)
pixi run docs-clean    # Clean build artifacts
```

**Code Quality:**

```bash
pixi run lint          # Check code with ruff
pixi run lint-fix      # Fix auto-fixable issues
pixi run type-check    # Check types with ty
```

**Git Hooks:**

```bash
pixi run hooks-install # Install pre-commit hooks
pixi run hooks-run     # Run hooks manually
pixi run hooks-update  # Update hook versions
```

### Testing Multiple Python Versions

The project supports Python 3.11-3.14 with version-specific environments:

```bash
pixi run --environment test-py311 test
pixi run --environment test-py312 test
pixi run --environment test-py313 test
pixi run --environment test-py314 test
```

[pydata-sphinx-theme]: https://pydata-sphinx-theme.readthedocs.io/en/stable/
