Docutils extensions
===================
Extensions for Python docutils.
May need latest docutils from SVN.

Docs below need a general clean up. Also see doc/.

Development targets
  - Du nodes and an rST directive for left- and right-margin page decoration.
  - An rST directive for table summaries.
  - An extended ``html4css1`` writer able to write these new nodes.
  - Testing experimental rST re-writer, see test/.
  - Various document transforms and settings 
    See `Transforms`_ (``dotmpe.du.ext.transform``).

  - These transforms are used by ``dotmpe.du.ext.reader.mpe.``\ `Reader`.
  - Several Nabu `Extractor`, `Storage` pairs, seel `Extractors`_ (``dotmpe.du.ext.extractor``).

  - ``dotmpe.du.form``\ `FormField`
  - ``dotmpe.du.builder`` has some packages with specific Reader/Parser/Writer
    component configurations, but frontend is undergoing work.

To be completed
  - extractor/form framework (esp. documentation)
  - rST forms. TODO: docs. The ``dotmpe.du.form``\ `FormProcessor`, used in transforms (``form1``) and extractors (``form2``).
    Forms allow for ``fields_spec`` which is used on the document tree like ``settings_spec`` is on argv. 
    Enable validation, feedback and more structured definitions of extractors.
  - rST directives for breadcrumbs.
  - TODO: docs. An inliner for the rST parser ``dotmpe.du.ext.parser.inliner``.

Also in this project some `notes on Du`__, and there are `some examples of rST and docutils`__ code.  
XXX: separate project? A first stab at a quick-reference chart for Du/rST, based in rST. See if combinable with sheet.


.. __: doc/main.rst
.. __: examples

dotmpe extensions
-----------------

Directives
''''''''''
Left and right page margin are decoration blocks (in addition to page header and footer).
There is at most one of each per page.

::

  .. margin:: left
  
     Margin contents left-side.
  
  .. margin:: right
     :class: my-doc
     
     Margin contents right-side.
  
  .. margin:: left
  
     More contents left-side.

Transforms
''''''''''
Docutils includes setting specs for some of its transforms into core and
frontend. The ``dotmpe.du.ext.reader.mpe`` Reader replaces some of these 
transforms with implementations that provide their own flexible 
settings spec.

.. include:: transforms.rst
   :start-after: .. 1 ---- 8< -----
   :end-before: .. 1 ---- >8 -----

.. start/end line requires du rev >= 6185

Read more about them in `Transforms`__

.. __: doc/transforms.rst

Extractors
''''''''''
.. include:: extractors.rst
   :start-after: .. 1 ---- 8< -----
   :end-before: .. 1 ---- >8 -----

Overview
--------
Work in progress
  - There is my own attempt at an rST writer, and in test/init.py the writer from
    Stefan's docutils branch is included. Not under active development but i hope to pick
    it up.

  - Before that happens I'm cleaning up code from some other docutils related projects.
    dotmpe.du.builder is shaping up nicely to be a collection of publishers for
    running in an server-environment. Maybe these can wrap some Nabu stuff
    (data-mining) later. Front-end development active in `Blue Lines`__.

.. __: http://blue-lines.appspot.com/

Other ToDo
  -  propose breadcrumb and other generate transforms on devel list
     Lea mentioned breadcrumbs.
  -  re-evaluate include, literal and raw dereferencing.
  -  ``--use-bibtex=USE_BIBTEX`` off latex2e may be nice practical example of external
     resource framework integration.
  -  directive options are not all i18n'd

What follows is some thoughts on document publishing.

Host-based publishing
----------------------
The standalone publisher works by deferring resource dereference to a host
system, i.e. the local filesystem. But

- there is no integrity checking,
- there is no explicit document base, or reconition of the document access
  protocol, and in short:
- there is no system for explicit document identification across protocols.

Standard Du works includes and stylesheets from files, and does not care what
references point to. 
The choice to only dereference local files is out of security consideration.

But here it misses conveniences that protocols can offer.
It does not at all register where content comes from, i.e. an include is evaluated
into a fully parsed document tree.
The document root that acts as an envelope, recording source and document id,
is discarded upon inclusion.
Also, multiple includes may create errors in case of ID's, e.g. `roles`
definitions collide.

.. XXX: see TODO 1


Examples
--------
- form demonstration
- example rSt on inline references and roles
- breakcrumbs

.. TODO: 

Log
-----
2010-11-04
  Stefan Merten published his xml2rST and included an installer.
  He also has rST2gxl 'producing GXL which can be transformed to dot'
  and rST2diff 'comparing two input files producing a marked up difference
  output'.
  See the `source directory`__

2010-12-01
    Integrating figure label patch by Alex @ du mailinglist.
    Created subclass of latex2e writter for this.

2011-01-12
  - Added summary directive and table attribute to comply with HTML4.
  - Made `write-up on link relations in reStructuredText`__.
  
.. __: src/python-docutils
.. __: doc/links.rst

