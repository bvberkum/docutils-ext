_example-thing-name-1

example-ref-name-1_

.. _example-ref-name-1: my-target_
.. _example-name-2: my-target_

.. _test: `my-target`_

Here come targets. 
The '`' appearantly forces the target into a paragraph.

_`example-target-id-1`

Test _`another target`.

This thing is with targets, except the above inline
targets, these change the following element.
All these here add an id or name to the below paragraph,
or lateron to below targets.

.. _example-name-3:

Text with target example-name-3.

This allows other elements with refid or refname to find them

XXX: not really sure about the status of id and name.

References. `example-name-5`__ and `example-name-5`_, or example-name-5_ 
is that the position where target with id Python was? Not really.
The reader/parser and writer transform the references. Here refuri
is spread to all target chains with as endpoint Python_.

Only the endpoint actually cathces new names/ids, 
it seems any one of refname, refid and refuri is an endpoint.

But what is refname vs refid? 
There is no refname here btw.

.. __: example-name-5_

**More references**. `test`__
And lets test `normal inline refs <./ref>`_ too and `anonymous inline refs <./ref>`__.
The former create two elements: inline reference and target.
The latter is not marked anonymous as the first one is, but implicitly is still "anonymous" as it has only name. 
You cant refer to these blank nodes with a reference name.
Its even more anonymous than the first, which cant be addressed either but still has an refid and a numberd target.


.. __: another-target-1_

One can share the reference from an inline reference because it gets a target,
and manually set one ore more ids for a named reference. As read here, where two IDs get the refuri from an inline
reference.

.. _test-2:
.. _test-1: `normal inline refs`_

.. _example-name-4:

.. |EXAMPLE| image:: images/biohazard.png

.. _example-name-5:
.. _my-target:
.. _Python: http://www.python.org/

.. _example-name-6:
.. _example-name-7:
.. _example-name-8: example-name-4_
.. _example-name-9: example-name-3_
.. _example-name-10: another-target-1_
.. _another-target-1:
.. _example-name-11: `another target`_

