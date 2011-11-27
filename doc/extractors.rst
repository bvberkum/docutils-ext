Extractors
-----------

Internal extractors

- DocId -> unid
- DuSettings -> 

Rationale
__________
Nabu Extractors are often paired with a Storage, but the implementation is
storage dependent.

Using ``zope.interface`` a more generic approach is implemented where the
extracted and stored data are single instances. Relations between types are
possible, though reference fields are of less importance at the moment than
actual primitive chunks of data. References may be these may be 'blank nodes',
but using URI is preferred.



.. 1 ---- 8< -----

``dotmpe.du.ext.extractor``
  ``form2.``\ `FormExtractor` and `FormStorage`
    TODO docs
  ``include.``\ `IncludeDoctree`
    TODO w.i.p.
  ``index.``\ `IndexRegistryExtractor`
    TODO w.i.p.
  ``inline.``\ `InlineExtractor`
    TODO w.i.p.
  ``reference.``\ `Extractor`
    TODO w.i.p.

.. 1 ---- >8 -----

