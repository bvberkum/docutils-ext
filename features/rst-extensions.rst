
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

.. _rST forms: `docs`_
.. _Transforms: doc/transforms.rst
.. _Extractors: doc/extractors.rst
.. _docs: doc/main.rst
.. _Blue Lines: http://blue-lines.appspot.com/

