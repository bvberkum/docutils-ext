

.. .. include:: utilities-json-outline.feature
   :code:

.. class:: feature-outline

Feature: An rst2outline utility with JSON output format
  Scenario: Convert definition list to JSON
    .. class:: inline-terms

    Given
      the current project,

    and
      a file "var/test-outline.1.json-1.rst" containing::

        Dev
          Embedded
            ..
          Barebone
            ..
          Web
            ..

      .. TODO: expand below to do proper json equiv test

    When
      the user runs::

        ./tools/rst-outline.py --outline test.json var/test-outline.1.json-1.rst

    Then
      file "test.json" should be created, and contain the same as "var/test-outline.1.json-1.json"

    When
      the user runs::

        ./tools/rst-outline.py --outline test.json var/test-outline.2.json-1.rst

    Then
      file "test.json" should be created, and contain the same as "var/test-outline.2.json-1.json"


.. .. raw:: html

   <style>
    dl.feature-outline > dd > div.first.line-block,
    dl.feature-outline > dd > dl > dd > div.first.line-block {
      padding: 1.5em 0;
    }
    /*
    dl.feature-outline > dt,
    dl.feature-outline > dd > div.first.line-block,
    dl.feature-outline > dd > div.first.line-block > div.line {
      display: inline;
    }
    */
    dl.inline-terms dt {
      /*clear: both; */
    }
    dl.inline-terms dt,
    dl.inline-terms dd,
    dl.inline-terms dd > p {
      display: inline;
    }
    dl.inline-terms dd {
      margin: 0;
    }
   </style>

