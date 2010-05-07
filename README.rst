Extensions for Python docutils (>= 0.5)

Development targets:
  - Directives for left- and right-margin decoration.
  - An ``html4css1`` writer with margin support.
  - Testing experimental rst writer, see test/
  - Some additional transforms with exposed settings are used in 
    ``dotmpe.du.ext.reader.mpe``.
  - ``dotmpe.du.builder`` has some packages with specific Reader/Parser/Writer
  	component configurations.


- Also in this project some `documentation on Du`__, and there are `some examples
  of rSt and docutils`__ code.  

.. XXX: separate project? A first stab at a quick-reference chart for Du/rSt, based in rSt.

.. __: doc/main.rst  
.. __: examples

dotmpe extensions
-----------------

Directives
''''''''''
Left- and right-margin are decoration blocks like the page header and footer.
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

.. include:: doc/transforms.rst
   :start-line: 3
   :end-line: 18

.. start/end line requires du rev >= 6185

Read more about them in `Transforms <doc/transforms.rst>`__.

Overview
--------
Source code sits in package ``dotmpe`` in the ``lib`` directory.

There is my own attempt at an rst writer, and in test/init.py the writer from
Stefan's docutils branch is included. Not under active development but i hope to pick
it up.

Before that happens I'm cleaning up code from some other docutils related projects.
dotmpe.du.builder is shaping up nicely to be a collection of publishers for
running in an server-environment. Maybe these can wrap some Nabu stuff
(data-mining) later. Front-end development active in `Blue Lines`__.

Working functionality is listed above in `dotmpe extensions`_. 

.. __: http://blue-lines.appspot.com/

Host publisher
--------------
Standalone publishing works by deferring resource derefentation to a host
system, e.g. the local filesystem or HTTP.

- There is no integrity checking.
- No explicit document base.
- No system for explicit document identification.

Within the publisher, it is best to restrict input and output channels not only
for security reason but also for simplicity. HTTP access adds things like
content-negotiation.

The overrides for these are include and subdoc, both access external
content, fine for controlled environments but does break standalone docs.

.. FIXME: I will have raw-url turned of in my reader?

Examples
--------
- form demonstration
- example rSt on inline references and roles

.. TODO: propose breadcrumb and other generate transforms on devel list
   Lea mentioned breadcrumbs.

.. TODO: 

