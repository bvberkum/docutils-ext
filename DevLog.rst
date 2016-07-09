DevLog
--------
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

2016-07-09
  - Taking up a little development again. Started adding and updating Docs.


.. __: doc/links.rst
.. _Blue Lines: http://blue-lines.appspot.com/
.. _Sitefile: //github.com/dotmpe/node-sitefile

