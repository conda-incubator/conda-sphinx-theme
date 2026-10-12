============
Example Page
============

This is an example page.

Example tables
==============

Hover over the links in the tables below to inspect the link hover color
in both light and dark mode. Table rows use alternating (zebra) backgrounds,
so the hover color needs to stay readable on each of them.

A simple table with a header row and links:

.. list-table:: Conda ecosystem projects
   :header-rows: 1
   :widths: 25 50 25

   * - Project
     - Description
     - Link
   * - conda
     - Cross-platform package and environment manager.
     - `conda docs <https://docs.conda.io/>`_
   * - conda-build
     - Build conda packages from recipes.
     - `conda-build docs <https://docs.conda.io/projects/conda-build/>`_
   * - conda-forge
     - Community-led collection of conda recipes.
     - `conda-forge <https://conda-forge.org/>`_
   * - conda-sphinx-theme
     - The Sphinx theme used by this documentation.
     - `GitHub <https://github.com/conda-incubator/conda-sphinx-theme>`_
   * - pixi
     - Package manager used to build this project.
     - `pixi docs <https://pixi.sh/>`_

The same kind of content as a grid table:

+------------+----------------------+---------------------------+
| Mode       | Hover color          | Contrast (WCAG AA >= 4.5) |
+============+======================+===========================+
| Light      | dark green           | 7.87:1 on white           |
+------------+----------------------+---------------------------+
| Dark       | light green          | 10.45:1 on dark surface   |
+------------+----------------------+---------------------------+
