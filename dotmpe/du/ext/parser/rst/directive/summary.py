"""reStructuredText summary directive.

In collaboration with transform.tables.TableSummary,
this allows to set the 'summary' HTML4.1 attribute on the neighbouring table.

Perhaps this should be deprecated by a 'table-caption' directive.
"""
from docutils import nodes
from docutils.parsers.rst import Directive, directives

from dotmpe.du.ext.transform import tables


# Directives for registration with docutils' rSt parser
class Summary(Directive):

    """
    Sets a summary for the neighbouring table.
    A pending node is added to be handled by transform later.
    """

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {  }

    def run(self):
        table_summary = ' '.join(self.arguments)
        node_list = []
        pending = nodes.pending(
            tables.TableSummary,
            {'summary': table_summary, 'directive': self.name},
            self.block_text)
        self.state_machine.document.note_pending(pending)
        node_list.append(pending)
        return node_list

