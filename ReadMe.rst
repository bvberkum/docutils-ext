Docutils extensions
===================
:Created: Aug. 2009
:Updated: Oct. 2015

Collection of extensions on Python docutils.
This document attempts to present an overview of the project tree.

A description is given of the command-line utilities in tools/,
then a list summary is given of the source code, whose main files will be
documented themselves. Lastly a global log and list of further references 
follows.

.. contents::

Utilities
---------
``tools/build.py``
  Can be symlinked to any publisher wanted, ie. rst2latex, etc.

  This should be the main entry point, but ``dupub.py`` (docutils publisher with
  extensions) may be (more) functional..

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
- `Docs`_
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
GIT
  master
    all development happened here until dev was branched.
  dev
    Sort of the master now. Testing only functional stuff, may be deceptive as
    not everything is unit/systemtested?

    :tests: 8 OK

    dev_rstwriterobjects
      separate development branch for rstwriter restructuring, 
      trying to OO-ify and add some elegance.

      :test: 57; 25 failures, 2 errors

    dev_simplemuxdem
      trying a lossless read/write using the rST SM base with a 
      simple text format, to understand the rSt parser statemachine.

      :tests: 2 OK

      Abandoned while I do get more insight into the rSt parser
      machinery.

    dev_form
      Splitting topic of dev for separate testing. Possibly a few hacks while
      core/frontend is in flux.

    dev_rstwriter
      While things left to be desired before finishing dev_rstwriterobjects,
      implement and test reStructuredText writer.

      :tests: 66, 9 failed

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

runs some of the modules in ``test/``. See ``test/main.list``.

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

Until then, the main body of tests is run by the ``rstwriter`` module,
running over all files from ``var/*demo.rst``. Lossy tests are implemented
by re-parsing the rST output, and doing (trying) a compare of the AST content 
and public attributes by generating and diff'ing the pseudoxml for both source and generated document. Iow. the test requires 3 publish actions, one of which the actually subject of test |---| that has the rST Writer component.


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
2009 September
  - Starting my own project for use with `Blue Lines`_, 
    custom 'margin' directives and HTML writer components.

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

2013 November
  - Retaking to development. 
  - Adding new tests. First unnittests for builder. 
    Need frontent/CLI system tests.
  - Splitting testing and non-functional stuff to sep. branches.
  - Adding build log and validation for test markup files.
    There should not be any log files in ``var/`` otherwise some test-file does not
    completely check out (``rm var/test-rst*.log && make test-validate-files``).

    Should clean/check out ``examples/`` too.

2014 August
  - Taking up Builder.process again for ~/htdocs.
    Started working on setup-file too, and considering Sitefile concept.

2015-03-28
  - Set up Sitefile_ as a Node.JS project. Maybe require Py Du extensions later
    but for now writing the concept there in JS/Coffee-Script. 
    
    Not really a builder. A frontend. Maybe a HTTP publisher, but it has no real builder or
    publisher component.
    Perhaps, rename it to Expressfile.

    Maybe want to investigate sitebuilder concept, ``wget -r`` and some patches would
    seem to suffice though.


.. __: doc/links.rst
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


