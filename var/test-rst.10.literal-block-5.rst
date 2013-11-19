As usual blocks need to be separated 
by white lines too.

.. parsed-literal::

   Foo *bar* **el** baz.

Then there is parsed literals (above), 
which loops back through the literal_block 
state in the rST statemachine parser, 
where all of the above blocks went
through too, but provides inline parsing.

> See this is a parsed *literal block* too

But::

  *this*, again is not as shown in 
  previous documents. Must be some 
  argument somewhere to that routine.

Test::

> Foo
> Bar

