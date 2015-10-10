
.. role:: test
   :class: strong emphasis literal

:test:`test`


This will confuse the parser, the emphasis3 ID is lost, replaced by 'role'.

.. role:: emphasis3(emphasis)
   :class: role

:emphasis3:`emphasis3`

.. role:: strong2(strong)
   :class: role

:strong2:`strong2`

.. role:: literal2(literal)
   :class: literal2 role

:literal2:`literal2`

Using the role name as first class name works, but rST does not currently write
directive+class names back.
