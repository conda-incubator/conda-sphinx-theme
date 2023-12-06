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

[pydata-sphinx-theme]: https://pydata-sphinx-theme.readthedocs.io/en/stable/
