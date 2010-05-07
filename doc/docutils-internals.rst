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


Du rSt
------

These are the most important inline markup constructs in Du.

- `Title reference`: `Title`.
- `Inline literal`: `Literal`
- `Anonymous reference`: Reference__

Title reference is the default inline interpreted text role.
Roles may be defined in hierarchies, see _`More roles` for the Du core
definitions.

Role definitions are not part of the result document, but seem to be a feature 
of the rSt parser.

More roles
-----------
Du defines 10__ of these. Each has a corresponding inline element, except that
PEP and RFC both use ``reference``. Custom roles that do not extend one of these
get inserted as ``inline`` elements.

- `emphasis`, :emphasis:`emphasis`
- `literal`, :literal:`literal`
- `strong`, :strong:`strong`
- `title-reference`, :title-reference:`title-reference`
- `pep-reference`, :pep-reference:`282`
- `rfc-reference`, :rfc-reference:`4287`
- `subscript`, :subscript:`subscript`
- `superscript`, :superscript:`superscript`  
- `abbreviation`, :abbreviation:`abbr.`
- `acronym`, :acronym:`acronym`

.. __: http://docutils.sourceforge.net/docs/ref/rst/roles.html

Standard roles
  .. role:: myrole
     :class: i-can-class-role
  
  - :myrole:`Some special text.`

  These roles are represented by the ``inline`` document node.

Raw line data  
  .. role:: raw-html(raw)
     :format: html

  - example :raw-html:`<span style="border:1px solid orange;">inline HTML</span>`

  ``raw`` inline nodes are inserted using the `format` directive option.

Extended roles  
  .. role:: mysubrole(emphasis)
  
  - `mysubrole` sub-classes emphasis: :myrole:`And other inline roles`.

  Such roles may redefinition of the respective document node by an additional
  class name.

----  

