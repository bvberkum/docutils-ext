Feature:
  | Represent Gherking formats in reStructuredText

  Background:
    | a literal "feature" document has an equivalent "rst" document in some style-variant

  Scenario Outline:
    | One based on definition list outlines, with minimal processing and styling
    | requirements but also minimal (rSt) structure

    ..

    | having
    | line blocks for parsable parts,
    | and literal blocks for multiline step arguments,
    | and example data tables identical to the original format.

    Given
      | an input "feature" document

    When
      | the "cmdline $feature" is run in an shell environment

    Then
      | the command output equals the "doc/rst-feature/$rst" document

    Examples:
      | <localname>                     | <base>     |
      | gherkin-example-001             | examples/  |
      | gherkin-example-002-backgrounds |            |
      | gherkin-example-003-outlines    |            |

