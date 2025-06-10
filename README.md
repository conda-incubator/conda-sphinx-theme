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

[pydata-sphinx-theme]: https://pydata-sphinx-theme.readthedocs.io/en/stable/
