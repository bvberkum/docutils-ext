
:build: @MKBUILD
:root: @MKROOT
:build: @MK_BUILD
:root: @MK_ROOT


.. figure:: /.build/project/docutils-ext/doc/builder-sequence.svg
  :target: /project/docutils-ext/doc/builder-sequence.pic

- `Description of transforms in this package`__
- `Description of extractors in this package`__
- `About linking in HTML and reStructuredText`__

.. __: transforms.rst
.. __: extractors.rst
.. __: links.rst

- `Original Du docs by Goodger on the transforms <du-transforms,cache.rst>`_
- `Misc. unsorted thoughts on docutils <docutils-suggestions.rst>`_
- `A short overview of Du   <docutils-internals.rst>`_
- `reStructuredText cheatsheet <sheet/du.rst>`_ a cheatsheet that could use some more cheats.
- `Other uses of Du/rSt     <third-party.rst>`__
- `of Du/rSt     <third-party.rst>`__

::

   .. not yet, this requires the subdoc branch of Du

   .. .. subdocument::

      - :file: introduction.rst
      - :file: docutils-internals.rst
      - :file: transforms.rst
      - :file: third-party.rst




dotmpe extensions
-----------------

.. _rST forms:

rST Forms
---------
See Components.rst#rst-forms-spec
- rST forms. TODO: docs.
  The ``dotmpe.du.form``\ `FormProcessor`, used in transforms (``form1``) and extractors (``form2``).

Forms allow for ``fields_spec`` which is used on the document tree like ``settings_spec`` is on argv.
Enable validation, feedback and more structured definitions of extractors.


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


