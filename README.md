# Conda Sphinx Theme

This is the Conda Sphinx Theme. It extends the [PyData Sphinx Theme][pydata-sphinx-theme]
project  by adding custom styling.

When creating a conda subproject you can include this theme by changing this
line in your conf.py file

```python
html_theme = 'conda_sphinx_theme'
```

And by including `conda_sphinx_theme` as a requirement in your documentation
installation.

To change the style, edit `conda_sphinx_theme/static/css/style.css`.

[pydata-sphinx-theme]: https://pydata-sphinx-theme.readthedocs.io/en/stable/