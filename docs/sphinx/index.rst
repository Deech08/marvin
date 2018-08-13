.. Marvin documentation master file, created by
   sphinx-quickstart on Sun Apr 10 08:50:42 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. title:: Marvin documentation

.. warning:: Marvin documentation is in the process of being restructured and improved. Some content can be missing while this task continue. In the meantime, please use the `stable version <http://sdss-marvin.readthedocs.io/en/stable/>`__ of the documentation. If you have suggestions to improve Marvin documentation, please `open an issue <https://github.com/sdss/marvin/issues/new/choose>`__.

|

.. image:: _static/logo5_lores.jpg
    :width: 600px
    :align: center
    :alt: MaNGA logo

|

Marvin Documentation
====================

Marvin is a tool specifically designed to visualise and analyse `MaNGA <https://www.sdss.org/manga>`_ data. It is developed and maintained by the MaNGA team. Marvin allows you to:

* Access reduced MaNGA datacubes local, remotely, or via a web interface.
* Access and visualise data analysis products.
* Perform powerful queries on data and metadata.
* Abstract the datamodel and forget where the data actually lives.
* Make good visualisation and scientific decisions by preventing common mistakes when accessing the data.

Marvin's code is publicly available in our `Github <https://github.com/sdss/marvin>`__ page. If you are using Marvin in any way (Web, API, or Tools) to do your science, please remember to :ref:`acknowledge and cite<marvin-citation>` us in your paper!

To install marvin simply run ``pip install sdss-marvin``. More details and known problem with installation can be found :ref:`here <marvin-installation>`.

.. note:: This documentation assumes that you are familiar with MaNGA data and its acronyms. If that is not your case, consider reading `this <https://www.sdss.org/manga/getting-started/>`_.

.. warning:: Marvin 2.x is the last version that will support Python 2.
  Marvin 3 and following will require Python 3.6+.


Getting Started
---------------

If you are new to Marvin check the following links before diving into the full documentation:

* The :ref:`lean tutorial <marvin-lean-tutorial>` is your quick start guide to Marvin.
* For quick reference, download the :ref:`cheatsheet <marvin-cheatsheet>`.
* :ref:`What's new in Marvin? <whats-new>`, :ref:`changelog <marvin-changelog>`, and :ref:`known issues <marvin-known-issues>`.
* Marvin uses `quantities <http://docs.astropy.org/en/stable/units/quantity.html>`_ to represent data (spectra, data cubes, etc). Here is a quick :ref:`introduction <marvin-quantities>`.
* More :ref:`tutorials <marvin-tutorials>` and :ref:`frequently asked questions <marvin-faq>`.


.. toctree::
   :maxdepth: 2
   :caption: Marvin at a Glance
   :hidden:

   installation
   whats-new
   tutorials/lean-tutorial
   cheatsheet
   tutorials/index
   known-issues
   faq


.. toctree::
   :maxdepth: 3
   :caption: User Docs

   tools/index
   query/index
   web
   api


.. toctree::
   :maxdepth: 3
   :caption: Datamodel

   datamodel/datamodels


.. toctree::
   :maxdepth: 2
   :caption: API/Code Reference

   reference/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`

* :ref:`search`
