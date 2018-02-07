Feature: build.py

  Scenario Outline: 
    When the user executes "<alias> --help"...
    Then `output` is not empty
    And `status` equals '0'

  Examples:
    | alias |
    | atlassian2html |
    | atlassian2pprint |
    | atlassian2rst |
    | atlassian2xml |
    | mime2html |
    | mime2pprint |
    | mime2rst |
    | mime2xml |
    | proc-dotmpe.du.builder.htdocs |
    | proc-dotmpe_v5 |
    | proc-htdocs |
    | proc-mpe |
    | proc-my.foo.lib |
    | pub-htdocs |
    | pub-mpe |
    | rst2atlassian |
    | rst2html |
    | rst2html-standalone |
    | rst2manpage |
    | rst2pprint-mpe |
    | rst2pprint-standalone |
    | rst2pseudoxml-dupub |
    | rst2xml-mkdoc |
    | rst2xml-mpe |
    | rst2xml-pep |
    | rst2xml-standalone |

    # FIXME: dupub-mkdoc
    # FIXME: dupub-mpe
    # FIXME: run-htdocs

#  Scenario Outline: every psuedoxml
#    When the user executes:
#    """
#    for t in var/test/test-rst*xml
#    do
#      <alias> $t
#    done
#    """
#    Then `status` equals '0'
#
