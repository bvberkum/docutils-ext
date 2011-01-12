""":created: 2011-01-12
"""
from docutils import nodes
from docutils.transforms import Transform


class TableSummary(Transform):

    """
    Move the summary value specified in the "pending" node into the
    immediately neighbouring table element.
    """

#    settings_spec = (
#            (
#            ))

    default_priority = 210

    def apply(self):
        assert self.startnode, "This transform should be run from a pending node. "
        pending = self.startnode
        parent = pending.parent
        index = parent.index(pending)
        table = None
        if index > 1 and \
                isinstance(parent[index-1], nodes.table):
            table = parent[index-1]

        elif index+1 < len(parent) and \
                isinstance( parent[index+1], nodes.table):
            table = parent[index+1]

        if table:            
            table['summary'] = pending.details['summary']
            parent.remove(pending)
            return

        error = self.document.reporter.error(
            'No suitable element following "%s" directive'
            % pending.details['directive'],
            nodes.literal_block(pending.rawsource, pending.rawsource),
            line=pending.line)

        pending.replace_self(error)



