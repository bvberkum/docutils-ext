Testing roles declarations and inline role spans a bit.


:emphasis:`emphasis`
:strong:`strong`
:literal:`literal`

.. role:: emphasis2(emphasis)

:emphasis2:`emphasis2`


----

Bug: the class must include the role as first name, or 
the result document will be incorrect. This works, but
see ./test-rst.5.inline-3-class-overrule-demo.rst how it does not.

However the rST writer output incorrect, atm. It does not output the role
directive and looses the classes.

.. role:: test
   :class: test strong emphasis literal

:test:`test`

----

.. Cf. normal inline syntax:

*emphasis* **strong** ``literal``

