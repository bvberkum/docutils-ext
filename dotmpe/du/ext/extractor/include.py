from dotmpe.du.ext import extractor


class IncludeDoctree(extract.Extractor):

    "TODO: Include nodes in doctree, resolves <include /> nodes. "
    "Optionally rewrite relative reference. "


    def apply(self, unid=None, store=None, alias=None, **kwds):
        pass


class RecordDependencies(Transform):

    ""

    settings_spec = ()

    default_priority = 500

    def apply(self):
        rv = DependenciesVisitor(self.document)
        rv.apply()


class DependenciesVisitor(nodes.SparseNodeVisitor):

    def apply(self):
        self.document.walkabout(self)

    def visit_include(self, node):
        pass


