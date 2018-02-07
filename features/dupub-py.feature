Feature: dupub.py

  Background:
    As long as ``build.py`` is not fully working, keep this as separate frontend
    for Docutils publisher component configurations.

  Scenario Outline:
    When the user executes "<alias> --help"...
    Then `output` is not empty
    And `status` equals '0'

  Examples:
    | alias |
    | rst2pprint |
    | rst2pseudoxml |
    | rst2rst |
    # FIXME | rst2rst-lossless |
    | rst2rst-mpe |
    | rst2xml |
