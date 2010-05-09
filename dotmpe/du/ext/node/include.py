"""reStructuredText remote include directive, which works on locally cached
remote resources. python-docutils extension.
"""
from docutils import nodes
from docutils.parsers.rst import directives



# Directive for registration with docutils' rSt parser
class RemoteInclude(directives.misc.Include):

    """
    This should leave an include node and run before 
    directives.misc.Include?
    """

    def run(self):
        pass


