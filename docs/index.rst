==============================================
Welcome to Conda Sphinx Theme's documentation!
==============================================

This is the Conda Sphinx Theme. It extends the ``pydata_sphinx_theme``
project https://pydata-sphinx-theme.readthedocs.io/en/stable/ by adding
custom styling.

When creating a conda subproject you can include this theme by changing this
line in your conf.py file

.. code-block:: python

   html_theme = 'conda_sphinx_theme'

And by including ``conda_sphinx_theme`` as a requirement in your documentation
installation.

Configuration for this demo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The full ``conf.py`` is

.. literalinclude:: conf.py

.. toctree::
   :hidden:
   :maxdepth: 1
   :titlesonly:

   example
