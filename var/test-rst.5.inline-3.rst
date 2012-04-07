.. testing roles declarations and inline role spans a bit

:emphasis:`emphasis`
:strong:`strong`
:literal:`literal`

.. role:: emphasis2(emphasis)

:emphasis2:`emphasis2`

.. role:: emphasis3(emphasis)
   :class: role

:emphasis3:`emphasis3`

.. role:: strong2(strong)
   :class: role

:strong2:`strong2`

.. role:: literal2(literal)
   :class: role

:literal2:`literal2`

----

.. role:: test
   :class: strong emphasis literal

:test:`test`

----

.. Cf. normal inline syntax:

*emphasis* **strong** ``literal``

