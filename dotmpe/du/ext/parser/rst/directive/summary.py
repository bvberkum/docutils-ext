"""reStructuredText summary directive and doc-tree node
"""
from docutils import nodes
from docutils.parsers.rst import Directive, directives

from dotmpe.du.ext.transform import tables


# Directives for registration with docutils' rSt parser
class Summary(Directive):

    """
    Embed a summary into the contained or neighbouring table.
    If the table is not in the contents, a pending node is added to be handled
    by transform later.
    """

    required_arguments = 1
    optional_arguments = 0
    has_content = True
    option_spec = {  }

    def run(self):
        table_summary = self.arguments[0]
        node_list = []
        if self.content:
            container = nodes.Element()
            self.state.nested_parse(self.content, self.content_offset,
                                    container)
            for node in container:
                if isinstance(node, nodes.table):
                    node['summary'] = table_summary
                else:
                    error = self.document.reporter.error(
                        'Unsuitable element in "summary" directive')

            node_list.extend(container.children)
        else:
            pending = nodes.pending(
                tables.TableSummary,
                {'summary': table_summary, 'directive': self.name},
                self.block_text)
            self.state_machine.document.note_pending(pending)
            node_list.append(pending)
        return node_list

