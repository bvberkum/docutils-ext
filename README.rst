Extensions for Python docutils (>= 0.5)

- left- and right-margin directive
- XHTML wirter with margin support   
- testing rst writer

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


.. footer::

   footer

.. header::

   header

Overview
--------
Source code sits in package ``dotmpe`` in the ``lib`` directory.

There is my own attempt at an rst writer, and in test/init.py the writer from
Stefan's docutils branch is included.
