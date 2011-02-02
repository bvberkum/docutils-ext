Docutils extensions
===================
:author: Berend (dotmpe)

My collection of extensions for Python docutils.
May need latest docutils from SVN.

Current focus is on finishing an rST writer component to make it possibly to
rewrite any doctree to reStructuredText format and do all kinds of new stuff.

Other development targets (done):
  - Left- and right-margin decoration.
  - Testing experimental rST re-writer ``dotmpe.du.ext.writer.rst``.
  - Various document transforms and additional document settings (with
    command-line options). See `Transforms`_ (``dotmpe.du.ext.transform``).
  - These transforms are used by ``dotmpe.du.ext.reader.mpe.``\ `Reader`.
  - Several Nabu `Extractor`, `Storage` pairs, see `Extractors`_ (``dotmpe.du.ext.extractor``).
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
  
.. __: doc/links.rst

.. _rST forms: `More docs`_
.. _Transforms: doc/transforms.rst
.. _Extractors: doc/extractors.rst
.. _Blue Lines: http://blue-lines.appspot.com/
.. _More docs: doc/main.rst
.. _Du/rST examples: examples/main.rst



