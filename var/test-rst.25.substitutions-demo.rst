Image substitution: |example|

The above reference is resolved in the output format. No way to know about it?

.. |EXAMPLE| image:: images/biohazard.png

The following use different notations for unicode characters that would be hard
to retrieve.
And also add a comment after the direct, that seems to be lost after parsing.

.. |---| unicode:: U+02014 .. em dash
   :trim:
.. |copy| unicode:: 0xA9 .. copyright sign
.. |tm| unicode:: U+02122 .. trademark sign


