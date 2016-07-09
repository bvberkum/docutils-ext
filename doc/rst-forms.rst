rST Forms
=========

Example::

  .. class:: form

  :Field name: Field value

Besides fields, other element nodes lend itself to use as forms.
See inline docs in ``dotmpe.du.form``.
See also `rST Forms spec`_ in Components.

Forms are defined by a sequence of form field specifications like::

  'id[,help];type[,require[,append[,editable[,disabled]]]][;vldtors,]',

which are parsed into FormField instances, that hold the data convertor and
validator.

With these, an optparse instance is used underneath for value parsing.
Current implementation matches a field definition either based on the class
or node id of an element.

Dev
---
- TODO: want an alternative to use a JSON schema parser and extract nested
  content. See dotmpe.du.form.DocumentFormVisitor.

- TODO: visit other elements than those with literal ID's.
  XXX: Since classes are a bit verbose to add, matching on field ID is
  easier. But it requires the schema to be more specific. Want a translator to add
  form field classes. Before invoking processor.


.. _rST Forms spec: Components#rst-forms-spec

