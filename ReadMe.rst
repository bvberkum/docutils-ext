Docutils extensions
===================
:author: Berend (dotmpe)

My collection of extensions for Python docutils.

Current focus is on finishing an rST writer component to make it possible to
rewrite any doctree to reStructuredText format and do all kinds of new stuff
with docutils.

This document attempts to present an overview of the project tree.
First a description is given of the command-line utilities in tools/,
second a list summary is given of the source code, whose main files will be
documented themselves. Lastly a global log and list of further references is
follows.

Utilities
---------
- tools/build.py can be symlinked to any publisher wanted, ie. rst2latex, etc.  

  This is the main entry point. 

Development targets
--------------------
Completed:
  - Left- and right-margin decoration.
  - Various document transforms and additional document settings (with
    command-line options). See `Transforms`_ (``dotmpe.du.ext.transform``).
  - These transforms are used by ``dotmpe.du.ext.reader.mpe.``\ `Reader`.
  - Several Nabu `Extractor`, `Storage` pairs, see `Extractors`_ (``dotmpe.du.ext.extractor``) but nothing complex yet.
  - `rST forms`_ framework.
    Use rST documents as forms, but gotten a bit out of use and no unittests.
    The implementation includes retrieving data from a document according to the
    `form specification`, which includes type conversion and value validation.

In progress:
  - ``dotmpe.du.builder`` has some packages with specific Reader/Parser/Writer
    component configurations, but frontend is undergoing work.
  - Front-end development in `Blue Lines`_.

ToDo
  -  re-evaluate include, literal and raw dereferencing.
  -  expose extractor and storage parameters on command line
  -  create a storage context that can provide Nabu stores. see extractors.rst_
  -  ``--use-bibtex=USE_BIBTEX`` from latex2e may be nice practical example of 
     external resource framework/metadata integration.
  -  directive options are not all i18n'd
  -  example: form demonstration
  -  example: example rSt on inline references and roles
  -  example: breakcrumbs
  -  rST directives for breadcrumbs.
  - `Docs`_
  - `Du/rST examples`_

Devel
  -  propose breadcrumb and other generate transforms on devel list,
     Lea mentioned breadcrumbs.
  -  Is the XML tree the complete representation whereof the rST is a variant,
     a perhaps lossy representation? 
     Attributes of Du's DOM (``docutiles.nodes``) maybe hidden.

Branches:
  master
    all development happened here until dev was branched.
  dev (current 2012-04-14)
    all development now here.

    :tests: 50; 21 failures, 29 OK

    dev_rstwriterobjects
      separate development branch for rstwriter restructuring, 
      trying to OO-ify and add some elegance.

      :test: 57; 25 failures, 2 errors, 30 OK

    dev_simplemuxdem
      trying a lossless read/write using the rST SM base with a 
      simple text format, to understand rSt parser.

      :tests: 53; 18 failures, 35 OK

      Abandonned while I do get enough insight into the rSt parser
      machinery.

rST writer
----------
An experimental writer. The module can be invoked as script using a rST filename
as argument, and will print some lossy and lossless testing results.

Currently only lossy rST writing is tested by 'make test'.
rST writer testcases are generated for all files matching 'var/test-*.rst'.

Getting Started
---------------
May need latest docutils from SVN.

For some automated tasks on this project package use ``make [help|..]``.
There is no setup script yet.

Log
-----
2010-11-04
  Stefan Merten published his xml2rST and included an installer.
  He also has rST2gxl 'producing GXL which can be transformed to dot'
  and rST2diff 'comparing two input files producing a marked up difference
  output'.

2010-12-01
  - Integrating figure label patch by Alex @ du mailinglist.
  - Created subclass of latex2e writter for this.

2011-01-12
  - Added summary directive and table attribute to comply with HTML4.
  - Made `write-up on link relations in reStructuredText`__.

2011-04-16
  - Updated testing so dynamic test cases (generated from file) are handled as
    usual by unittest.main, no more need to aggregate testsuites.
    Lossless testing is disabled for now.

- `Issues <Issues.rst>`_

.. __: doc/links.rst

.. _rST forms: `docs`_
.. _Transforms: doc/transforms.rst
.. _Extractors: doc/extractors.rst
.. _Blue Lines: http://blue-lines.appspot.com/
.. _docs: doc/main.rst
.. _Du/rST examples: examples/main.rst



