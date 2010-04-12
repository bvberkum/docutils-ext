Extensions for Python docutils (>= 0.5)

Development targets:
  - Directives for left- and right-margin decoration.
  - A ``html4css1`` writer with margin support.
  - Some additional transforms with exposed settings.  
  - Testing experimental rst writer
  - an experimental publisher for a web-service to enable rSt content on 
    non-Python hosts. 

    .. Perhaps data extraction and cross-referencing in the future.
       integration with nabu


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
   :start-line: 0
   :end-line: 15

.. start/end line requires rev >= 6185

Read more about them in `Transforms <doc/transforms>`__.

Overview
--------
Source code sits in package ``dotmpe`` in the ``lib`` directory.

There is my own attempt at an rst writer, and in test/init.py the writer from
Stefan's docutils branch is included. Not under active devel but i hope to pick
it up sometime.

Frontend and pub contain an experimental adapted version of the Du publisher and core
utils. Active development based on the ideas below. 

Working functionality is listed above in `dotmpe extensions`_. 


Docutils publishing
-------------------
.. note::

   This is a short overview of the docutils publisher.

The Docutils publisher reads stream data from source, parses this to a raw tree, 
transforms it into some document structure and finally writes that structure to
an output format.

All components in the publication chain (source, reader, parser, writer, destination)
may contribute transforms and reference resolvers. 

Transforms are mainly used by parser and reader to structure and index the
document from its raw text-based data. Transforms are loaded and applied after 
reading and parsing has completed.

Source and destination are Input and Output components that work on encoded 
character streams. 

Each Component is a SettingsSpec and TransformSpec.
A TransformSpec list transforms and unknown reference resolvers.
A SettingsSpec may be loaded into OptionParser, but Input and Output are
excluded right now. Path or id, and io encoding and codec error handlers are
rather handled in the core and defined by frontend.

In the core, Publisher is the facade used by front-end tools.
It handles the main components, Reader, Parser and Writer and the publication
cycle from source to destination using settings and transforms. 
The settings are loaded from config, CLI and may be programmatically
defined. Available settings are defined by the different components.


Remote publisher
----------------
Std Du has a standalone reader and some minor variants.
Standalone meaning operating on a single file, within a local filesystem?

The remote reader would be another variant that reads remote resources.
Likewise, a host could provide a specific writer for certain documents.

That means:

- add content Resolver for source to settings. 
  Each resolver could be a factory for Input or Output components resp.?
  
  (In addition to a path, Input and Output also have encoding
  parameters with some form of codec error-handling.)

.. XXX: What about language, and even content-type may be part of the document
		retrieval protocol layer.

- make this resolver available in something related to unknown_reference_resolvers, 
  because inclusion based transforms will need it too. 

  The current include directive in rst will need to be rewritten, to say use
  document.transformer.content_resolver.

- Add settings to restrict hosts, ie. each ID needs to be resolved and 
  bound/specify a host.

The source can be an absolute or relative reference, depending
on the chosen resolver, it probably should always be converted to a global
reference, possibly with id?
Destination may need to be dereferenced in a similar way.

Also, publishing from one host to another requires rewriting of references. 
A publisher could only handle that if for both source and destination host 
there was a matching Reader and Writer combination. 

Back `in 2004 there was a great post`__ on the mailing list about handling of
references in docutils. 

.. __: http://thread.gmane.org/gmane.text.docutils.devel/2060/focus=2066


Host publisher
--------------
Standalone publishing works by deferring resource derefentation to a host
system, e.g. the local filesystem or HTTP.

- There is no integrity checking.
- No explicit document base.
- No system for explicit document identification.

