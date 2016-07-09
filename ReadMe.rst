Docutils extensions
===================
:Created: Aug. 2009
:Updated: Jun. 2016
:Version: 0.0.1

:Status:

  .. image:: https://secure.travis-ci.org/dotmpe/docutils-ext.png?branch=test
    :target: https://travis-ci.org/dotmpe/docutils-ext/branches
    :alt: Build

  .. image:: https://badge.fury.io/gh/dotmpe%2Fdocutils-ext.png
    :target: http://badge.fury.io/gh/dotmpe%2Fdocutils-ext
    :alt: GIT


:rST writer:

  .. image:: https://secure.travis-ci.org/dotmpe/docutils-ext.png?branch=test-rstwriter
    :target: https://travis-ci.org/dotmpe/docutils-ext/branches
    :alt: Build


Collection of extensions on Python docutils.
This document attempts to present an overview of the project tree.

A description is given of the command-line utilities in tools/,
then a list summary is given of the source code, whose main files will be
documented themselves. Lastly a global log and list of further references
follows.

.. contents::


Features
---------
Utilities
  - Command line user tools.

rST Extensions
  - Additional Du components.

rST Writer
  - Work in progress lossy rST writer for rst2rst publish.

rST Outlines
  - Planning: Extract outlines from rST. See `Feature: Outlines`__


.. __: features/outlines.features


Development
-----------

Completed
'''''''''
- Left- and right-margin decoration.
- Various document transforms and additional document settings (with
  command-line options). See `Transforms`_ (``dotmpe.du.ext.transform``).
- These transforms are used by ``dotmpe.du.ext.reader.mpe.``\ `Reader`.
- Several Nabu `Extractor`, `Storage` pairs, see `Extractors`_ (``dotmpe.du.ext.extractor``) but nothing complex yet.
- `rST forms`_ framework.
  Use rST documents as forms, but gotten a bit out of use and no unittests.
  The implementation includes retrieving data from a document according to the
  `form specification`, which includes type conversion and value validation.
- Monkey patched ``docutils.{readers,parser,writers}.get_*_class()`` to load
  components from my lib. Enable 'extension' by importing ``dotmpe.du.ext``.

In progress
'''''''''''
- ``dotmpe.du.builder`` has some packages with specific Reader/Parser/Writer
  component configurations, but frontend is undergoing work.
- Front-end development in `Blue Lines`_. Simplified frontend for NodeJS.
- rST rewriter.

ToDo
''''
-  re-evaluate include, literal and raw dereferencing.
   want something like subdocs but low on the list of wannahaves.
-  expose extractor and storage parameters on command line as other
   components.
-  create a storage context that can provide Nabu stores. see Extractors_
-  ``--use-bibtex=USE_BIBTEX`` from latex2e may be nice practical example of
   external resource framework/metadata integration.
-  directive options are not all i18n'd
- `Du/rST examples`_

  -  example: form demonstration
  -  example: example rSt on inline references and roles
  -  example: breakcrumbs

-  rST directives for breadcrumbs, testing etc? options?
- `Issues`_


Devel
''''''''''
-  Started docs per feature, to document specs, work to test scenarios.
-  Fix accum. cruft in `Docs`_
-  Validation. Relax-NG?
-  I'd like an alternative (even less vertically hungry) markup for titles.
   What about ``=== title`` or ``= title =`` block formats. Nice and short
   where appropiate.
-  Same point goes for tables (title would be header, left or right aligned etc.)
   If rstwriter restructured is finished I might have stab at this.
-  propose breadcrumb and other generate transforms on devel list,
   Lea mentioned breadcrumbs (long ago..).
-  Is the XML tree the complete representation whereof the rST is a variant,
   a perhaps lossy representation? I think it loses some things, should keep
   track during rstwriter devel.


Branches
''''''''
.. include:: BranchDocs.rst
   :start-line: 3

rST writer
----------
Although still heavily a work in progress, I think it may be almost ready for
simple rST-to-rST processes... should push through.
Tables may be low on the wishlist though, get everything else first.
Then figure out nested parser for tables. Perhaps need to think about nested
writer for current literal blocks already?

Getting Started
---------------
- May need latest docutils from SVN, sorry not sure about current version
  but Du has not been in a lot of flux so..
- For some automated tasks on this project package use ``make [help|..]``.
- There is no setup script yet.
- Skim the `docs`_.

Testing
-------
::

  make test

runs some of the modules in ``test/``. See ``test/main.list`` for which.

The main development is at the rST writer. All test files are located in ``./var``,
basicly the bulk of the tests are based on comparison of output from the Du publisher.

This is the simplest way to test for absolute equivalent documents, ie.
'lossless' publisher transormations. But that is quite a requirement, and probably
only applies to the ``rst2rst`` chain. I think fully lossless representation at this point should be considered more of a convenience than requirement\ [*]_. The 'lossless' test approach is however suited to test the behaviour of chains of Parser, Reader, and Transform components when used with the ``pseudoxml`` writer.

So for testing of a document publisher, a check for all the content from the
source manuscript is the first device to have. What we really need is a Xanadu-esque
demuxer, to tell us which are the metacharacters, and what the corpus\ [*]_.
Maybe a writer that only picks out the character-data is something to be
explored for testing.

Until then, the main body of tests is run by the ``rstwriter`` module, running over all files from ``var/*.rst``. Test files are named and divided into seperate syntax topics.

Lossy tests are implemented by re-parsing the rST output, and doing (trying) a compare of the AST content and public attributes by generating and diff'ing the pseudoxml for both source and generated document. Iow. the test requires 3 publish actions, one of which the actually subject of test |---| that has the rST Writer component.


.. [*] It will quite possibly require additional properties on the AST to support true lossless ``rst-to-rst``, since not all rST syntax choices are of consequences in other representations (ie. indentation depths). Rather, a rst2rst publisher may serve to normalize formatting, and also to run some transforms to reorder, renumber, rename, cross-reference, etc.

.. [*] But we don't have one of those really. Until there is established and
   accepted one, while virtually all modern virtual representation is an
   inseperable mix of text and context.

   The functionality of 'hyper'-text was defined long ago, as the relation of
   arbitrary spans of text. Three sets of them: the subject, predicate and object.
   This radically abstract method of hyperlinking is essentially what Xanadu '88 (now known as Green) was.

   .. It is from such interoperable base, that an entirely new medium can arise of
      not seen before level of expression. And it will be screaming for consencus,
      for acception and rejection, sharing and keeping, generalizing or specifying.


The module is used as a crude test script during bugfixing::

  python dotmpe/du/ext/writer/rst.py [\*.rst]

This prints the documents in source and psuedoxml, conveniently side-by-side.

Currently only lossy rST writing is tested by 'make test' because
that generates enough work and bugreports for now.

rST writer testcases are generated for all files matching ``var/test-*.rst``.


Dependencies
''''''''''''
::

  pip install coverage


- some symlinks in lib/
- my mkdocs project to build from ``Rules.mk``
- xmllint

Log
-----
.. include:: DevLog.rst
   :start-line: 3


.. _Issues: Issues.rst
.. _rST forms: `docs`_
.. _Transforms: doc/transforms.rst
.. _Extractors: doc/extractors.rst
.. _Blue Lines: http://blue-lines.appspot.com/
.. _docs: doc/main.rst
.. _Du/rST examples: examples/main.rst
.. _Sitefile: //github.com/dotmpe/node-sitefile

.. |---| unicode:: U+02014 .. em dash
   :trim:
.. |copy| unicode:: 0xA9 .. copyright sign
.. |tm| unicode:: U+02122 .. trademark sign
.. |date| replace:: Date!


