Extractors
-----------

htdocs
  - tinkering
reference
  - uriref only for now
logbook
  - journal keeper for rst content
include
  - dependency resolving extractor?
inline
  - to-be generic role indexer?
index
  - another indexer try

Rationale
__________
Nabu Extractors are often paired with a Storage, but the implementation is
storage dependent.

Using ``zope.interface`` a more generic approach may implemented.

1. where the extracted and stored data are distinct componets or instances 
   of and adapters do the transforming and writing. 
2. var. schemes using the above



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

