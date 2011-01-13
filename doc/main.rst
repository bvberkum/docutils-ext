
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

- `Original Du docs by Googder on the transforms <du-transforms,cache.rst>`_
- `Misc. unsorted thoughts  <docutils-suggestions.rst>`_
- `A short overview of Du   <docutils-internals.rst>`_
- `reStructuredText cheatsheet <sheet/du.rst>`_ a cheatsheet that could use some more cheats.
- `Other uses of Du/rSt     <third-party.rst>`__

::

   .. not yet, this requires the subdoc branch of Du

   .. .. subdocument::
   
      - :file: introduction.rst
      - :file: docutils-internals.rst
      - :file: transforms.rst
      - :file: third-party.rst
