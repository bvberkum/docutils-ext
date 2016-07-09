rST Forms
=========

Example::

  .. class:: form

  :Field name: Field value

Besides fields, other element nodes lend itself to use as forms.
See inlin docs in ``dotmpe.du.form``.
See also `rST Forms spec`_ in Components.

Forms are defined by a sequence of form field specifications like::

  'id[,help];type[,require[,append[,editable[,disabled]]]][;vldtors,]',

With these, an optparse instance is used underneath for value parsing.
Current implementation matches a field definition either based on the class
or node id of an element.

TODO: want an alternative to use a JSON schema parser and extract nested
content.


.. _rST Forms spec: Components#rst-forms-spec

