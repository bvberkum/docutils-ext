Docutils extensions
===================
:author: Berend (dotmpe)

My collection of extensions for Python docutils.
May need latest docutils from SVN.

For some automated tasks on this project package use ``make [help|..]``.
There is no setup script yet.

Current focus is on finishing an rST writer component to make it possible to
rewrite any doctree to reStructuredText format and do all kinds of new stuff
with docutils.

Other development targets (done):
  - Left- and right-margin decoration.
  - Various document transforms and additional document settings (with
    command-line options). See `Transforms`_ (``dotmpe.du.ext.transform``).
  - These transforms are used by ``dotmpe.du.ext.reader.mpe.``\ `Reader`.
  - Several Nabu `Extractor`, `Storage` pairs, see `Extractors`_ (``dotmpe.du.ext.extractor``) but nothing complex yet.
  - `rST forms`_ framework.
    Use rST files as forms, but gotten a bit out of use and no unittests.
  - ``dotmpe.du.builder`` has some packages with specific Reader/Parser/Writer
    component configurations, but frontend is undergoing work.
  - Front-end development in `Blue Lines`_.

ToDo
  -  propose breadcrumb and other generate transforms on devel list,
     Lea mentioned breadcrumbs.
  -  re-evaluate include, literal and raw dereferencing.
  -  ``--use-bibtex=USE_BIBTEX`` from latex2e may be nice practical example of 
     external resource framework/metadata integration.
  -  directive options are not all i18n'd
  -  example: form demonstration
  -  example: example rSt on inline references and roles
  -  example: breakcrumbs
  -  rST directives for breadcrumbs.
  - `Docs`_
  - `Du/rST examples`_


rST writer
----------
An experimental writer. The module can be invoked as script using a rST filename
as argument, and will print some lossy and lossless testing results.

Currently only lossy rST writing is tested by 'make test'.
rST writer testcases are generated for all files matching 'var/test-*.rst'.

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



