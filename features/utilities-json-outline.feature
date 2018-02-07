Feature: a rst2outline utility with JSON output format

  Background:
    This is an ad-hoc utility testing the ``dotmpe.du.ext.writer.outline``
    component.

    It duplicates some code from ``dotmpe.du.ext.transform.outline`` and its
    not certain a separate outline writer is needed.


  Scenario Outline: Convert definition list to JSON

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
    And no file "test.json" exists

    When the user runs:
      """
      ./tools/rst-outline.py <rst>
      """
    Then `output` should equal contents of "<json>"
    And no file "test.json" exists

    When the user runs:
      """
      ./tools/rst-outline.py --outline test.json <rst>
      """
    Then file "test.json" should be created, and contain the same as "<json>"
    And `output` should equal contents of "<json>"

    When the user runs:
      """
      ./tools/rst-outline.py --outline test.json <rst>
      """
    Then "test.json" is created, same contents as "<json>"
    And `output` equals "<json>" contents

		And cleanup "test.json"

  Examples:
      | rst | json |
      | var/test-outline.1.json-1.rst | var/test-outline.1.json-1.json |
      | var/test-outline.2.json-1.rst | var/test-outline.2.json-1.json |

