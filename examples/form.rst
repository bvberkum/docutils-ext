Example Form
""""""""""""

See test/form.py.

Supported
'''''''''

.. Plain lists

:my cs-list: 1,two, 3, and four
:my ws-list: 1 2 3

.. Du list variants:

my du list
  - 1
  - 2  

.. note that both field and definition list above are noted as form-field 
   because the nameid matches. Same goes for the following section

Du Tree
----------
.. some nested freaks.. testing. 

:My Du tree:
    - - nesting test 1.1
      - test 1.2

    - - 2.1
      - 2.2
      - - - 2.3.1.1

    - 3
    - - 4.1
      - - - - - - 4.2.1.1.1.1.1
        - 4.2.2
        - 4.2.3

.. And what exactly makes up the body of the section-form-field?
   see wat convertors can do perhaps.

Supported Cont'd
""""""""""""""""

:my du tree 2:
    - branch 1

      - branch 1.1

        - leaf 1.1.1
        - leaf 1.1.2  

      - leaf 1.2  
      - leaf 1.3

    - branch 2
    - branch 3

      - leaf 3.1
      - leaf 3.2




.. :my uri:                http://docutils.sourceforge.net/

.. :my integer percentage: 99%

.. class:: form

:my string:             test
:my integer:            +123
:my yesno:              yes 
:my flag: 
:my exclusive flag:
:my unsigned integer:   d
:my unknown: entry
:my colour:             red


Unsupported
''''''''''''

.. option lists

--opt-str opt-arg
    opt-descr

--opt, -o
    testing


term
    definition
term
    term
        definition
    term
        definition

----

.. intentional build error:

x
xx
 x

 
