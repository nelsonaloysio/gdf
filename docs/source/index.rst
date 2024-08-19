.. toctree::
   :hidden:
   :caption: Introduction

   Overview <self>

.. toctree::
   :hidden:
   :caption: Main documentation

   api

.. note::

   This documentation was generated on |today| for package release |release|.


########
Overview
########

**NetworkX-GDF** extends the `NetworkX <https://networkx.org>`__ library to support GDF (Graph Data
Format) files.

It provides two functions to read and write GDF files, which are commonly used to
store graph data in a tabular format. The package is designed to be lightweight on requirements and
easy to use.

Install
=======

The package is readily available from `PyPI <https://pypi.org/project/networkx-gdf/>`_:

.. code-block:: bash

   $ pip install networkx-gdf

It supports **Python 3.7+** and has been tested on Linux, Windows, and macOS.


Quick start
===========

The following is a quick example of the package in action, covering its basic functionality.

.. code-block:: python

   >>> from networkx_gdf import read_gdf, write_gdf
   >>>
   >>> # Reads NetworkX graph object from file.
   >>> G = read_gdf("input_file.gdf")
   >>>
   >>> # Writes NetworkX graph object to file.
   >>> write_gdf(G, "output_file.gdf")

For details on the functions above and the package's usage, please refer to the `API Reference <api.html>`_ page.

.. seealso::

   The package's `GitHub repository <https://github.com/nelsonaloysio/networkx-temporal>`_ for the latest updates and issues. Contributions are welcome!
