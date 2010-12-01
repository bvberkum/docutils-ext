Example Form
""""""""""""

See test/form.py.

Supported
'''''''''

.. Plain lists

:My CS-List: 1,two, 3, and four
:My WS-List: 1 2 3

.. Du list variants:

My Du List
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

:My Du tree 2:
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

.. :My uri:                http://docutils.sourceforge.net/
.. :My integer percentage: 99%

.. class:: form

My string
    test
My integer
    +123
My yesno
    yes 

.. class:: form

:My flag: 
:My exclusive flag:
:My unsigned integer:   d
:My unknown: entry
:My colour:             red

:My error:   str

Unsupported
''''''''''''

.. option lists?

--opt arg      opt-descr
--opt, -o      testing
--opt=val, -f value
    opt-descr


