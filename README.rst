docutils-ext.mpe
================
Extensions for Python docutils (>= 0.5)

Development targets:
  - RSt parser directives for left- and right-margin decoration.
  - An ``html4css1`` writer with margin support.
  - Testing experimental rst writer, see test/
  - Some additional transforms with exposed settings are used in 
    ``dotmpe.du.ext.reader.mpe``.
  - ``dotmpe.du.builder`` has some packages with specific Reader/Parser/Writer
    component configurations.

- Also in this project some `documentation on Du`__, and there are `some examples
  of rSt and docutils`__ code.  

.. XXX: separate project? A first stab at a quick-reference chart for Du/rSt, based in rSt. See if combinable with sheet.

To use the extensions, change from the standard du components to those in 
``dotmpe.du.ext.*``. There may not be a ready-to-use frontend, or even a
suitable reader for your purposes here. 
Mostly it is a place to keep my own particular component/transform
configurations, and experiment with some new ones. 
There is some incomplete code for frontend support, but mainly that is to enable
another publisher project, `Blue Lines`. 

However other additions by this project may be compatible with the interests of the
Du project itself, ie. might be contributed. 


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

TODO
  -  propose breadcrumb and other generate transforms on devel list
     Lea mentioned breadcrumbs.
  -  re-evaluate include, literal and raw dereferencing.
     

What follows is a discussion of document publishing and exploration of what
management is needed.

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

Misc
-----
2010-11-04
  Stefan Merten published his xml2rst and included an installer.
  He also has rst2gxl 'producing GXL which can be transformed to dot'
  and rst2diff 'comparing two input files producing a marked up difference
  output'.
  See the `source directory <~/src/python-docutils>`__



