Feature: a rst2outline utility with JSON output format

  Scenario: Convert definition list to JSON

      Given the current project,

      And a file "var/test-outline.1.json-1.rst" containing:
        """
        Dev
          Embedded
            ..
          Barebone
            ..
          Web
            ..
        """

      # TODO: expand below to do proper json equiv test

      When the user runs:
        """
        ./tools/rst-outline.py --outline test.json var/test-outline.1.json-1.rst
        """

      Then file "test.json" should be created, and contain the same as "var/test-outline.1.json-1.json"


      When the user runs:
        """
        ./tools/rst-outline.py --outline test.json var/test-outline.2.json-1.rst
        """

        Then file "test.json" should be created, and contain the same as "var/test-outline.2.json-1.json"


