
This is a mini-specification of interpreting a literal specification, intended
as a processable design document as part of an project task.


Its goals are:

- provide a JSON representation, describing the document within the schema of an
  outline format,

- provide one or more reStructuredText representation, for integration in
  and rendering/publishing by Docutils-based documentation systems or ports.


Design
------
The content format is based on Gherkin_.

Background
__________
It has a fixed set of hierarchical elements, starting at a feature, scenario(s),
and given/when/then/and rules or conditions. Rules contain inline markup to
provide the processor with prescribed structures, and processors usually employ
regular expression to match these with routines and specific fields for argument
and keyword settings.

The format has a hierarchical structure, but its elements are line based,
allowing simple ad-hoc processing. Exact literal format and level of parsing
varies,

XXX: calling for both a set of specific governing grammar and syntax rules, and liberal implementations.

Formats are based on conventions. Usually defaulting to the preferred syntax of
certain languages for e.g. literal inline single or multiline strings. Also
some but not all may allow for certain variations, like the support for inline
multiline content.

Standard variations include:

- background-section_\ 's to provide a sequence that is required before each
  scenario.

- scenario-outline_\ 's to provide a set of example data rows, and one template, to specify a recurring scenarios. Depending on the level of implementation, this could also be used to lift data at run-time from some other source than the feature document.


.. _Gherkin: https://github.com/cucumber/cucumber/wiki/Gherkin
.. _background-section: https://github.com/cucumber/cucumber/wiki/Background
.. _scenario-outline: https://github.com/cucumber/cucumber/wiki/Scenario-Outlines


TODO: more on design decisions, limitations, also issues section


Implementation
--------------

.. .. require:: features/gherkin-processing.feature


first, examples lifted from the Cucumber wiki are described in rSt.

- examples/gherkin-example-001.feature
- examples/gherkin-example-002-backgrounds.feature
- examples/gherkin-example-003-outlines.feature

.. include:: ./rst-feature/gherkin-example-001.rst


In addition,

Feature:
  | Describe Some terse yet descriptive text of what is desired

  ..

  | Textual description of the business value of this feature

  Scenario:
    | Matching and structuring scenario rules

    Given
      | any precondition, action or postcondition using `literal` "inline" 'markup' as desired

      And
        | With

        ::

          multiline inline literal
            content akin to
          HEREDOC-style constructs

    When
      | a feature parser is instantiated to automate the processing of a specification

    Then
      | it requires a context that maps rules to, and implements its execution


Use Cases
---------

.. .. require:: ../features/rst-features.feature

.. include:: ./rst-feature/rst-feature.rst

