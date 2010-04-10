Extensions for Python docutils (>= 0.5)

- left- and right-margin directive
- XHTML wirter with margin support   
- testing experimental rst writer
- experiments in alternative frontend/publishers  

dotmpe extensions
-----------------
The following new directives:

.. margin:: left

   Margin contents left-side.

.. margin:: right
   :class: my-doc
   
   Margin contents right-side.

.. margin:: left

   More contents left-side.

.. Just to illustrate the relation in output, the header and footer:

.. footer::

   footer

.. header::

   header

Overview
--------
Source code sits in package ``dotmpe`` in the ``lib`` directory.

There is my own attempt at an rst writer, and in test/init.py the writer from
Stefan's docutils branch is included. No under active devel but i hope to pick
it up sometime.

Frontend and pub contain an experimental adapted version of the Du publisher and core
utils. Active development based on the ideas below. The purpose being to offer
an publisher web-service to enable rSt content on non-Python hosts. Perhaps data
extraction and cross-referencing in the future.

Remote publisher
----------------
Std Du has a standalone reader and some minor variants.
Standalone meaning operating on a single file, possibly within a filesystem.

The remote publisher is another variant that should be able to handle remote sources.

This means:

- adapt rst parser to use different impl. for include directive
- adapt publisher to handle URL IO. possibly restrict hosts.
  possibly add Resolver factory component with resolvers on multiple protocols.

Host publisher
--------------
Standalone publishing works by deferring resource derefentation to a host
system, e.g. the local filesystem or HTTP.

- There is no integrity checking.
- No explicit document base.
- No explicit document identification.

