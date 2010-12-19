import sys
from docutils.parsers.rst import states


debug = sys.stderr
#debug = open('log','w+')

class Inliner(states.Inliner):

    def __init__(self):
        states.Inliner.__init__(self)

    def init_customizations(self, settings):
        states.Inliner.init_customizations(self, settings)
        if settings.title_directory:
            self.titles = None # TODO: load indices

    def inline_obj(self, match, lineno, end_pattern, nodeclass,
                restore_backslashes=0):
        """
        Find:

        - literal
        - target
        - emphasis
        - strong
        - substitution_reference
        """
        strstart, nodes, strend, msgs, s = states.Inliner.inline_obj(self, match,
                lineno, end_pattern, nodeclass,
                restore_backslashes=restore_backslashes)
        #print >>debug, "inline_obj", nodes
        return strstart, nodes, strend, msgs, s

    def interpreted(self, rawsource, text, role, lineno):
        """
        Find:

        - title_reference
        - inline (role)
        """
        nodes, msgs = states.Inliner.interpreted(self, rawsource, text, role, lineno)
        #print >>debug, "interpreted", nodes
        return nodes, msgs

    def standalone_uri(self, match, lineno):
        """
        Find:

        - reference (http, mailto, etc.)
        """
        nodes = states.Inliner.standalone_uri(self,
                match, lineno)
        #print >>debug, "standalone_uri", nodes
        return nodes

    def phrase_ref(self, before, after, rawsource, escaped, text):
        """
        Find:

        - reference
        """
        before, nodes, after, msg = states.Inliner.phrase_ref(self, before,
                after, rawsource, escaped, text)
        #print >>debug, "phrase_ref", nodes
        return before, nodes, after, msg

    def implicit_inline(self, text, lineno):
        "Find in-between normal text"
        nodes = states.Inliner.implicit_inline(self, text, lineno)
        #print >>debug, "implicit_inline", nodes
        return nodes

# XXX:BVB: dont know why but these do not get called:

#    def inline_internal_target(self, match, lineno):
#        strstart, nodes, strend, msg = states.Inliner.inline_internal_target(self, match, lineno)
#        print >>debug, "inline_internal_target", nodes
#        return strstart, nodes, strend, msg
#
#    def footnote_reference(self, match, lineno):
#        strstart, nodes, strend, msgs = states.Inliner.footnote_reference(self,
#                match, lineno)
#        print >>debug, "footnote_reference", nodes, msgs
#        return strstart, nodes, strend, msgs
#
#    def interpreted_or_phrase_ref(self, match, lineno):
#        strstart, nodes, strend, msg = states.Inliner.interpreted_or_phrase_ref(self, match, lineno)
#        print >>debug, "interpreted_or_phrase_ref", nodes, msgs
#        return strstart, nodes, strend, msg

#    def reference(self, match, lineno, anonymous):
#        strstart, nodes, strend, msg = states.Inliner.reference(self, match,
#                lineno, anonymous)
#        print >>debug, "reference", nodes, msg
#        return strstart, nodes, strend, msg
#
#    def anonymous_reference(self, match, lineno):
#        strstart, nodes, strend, msg = self.reference(match, lineno, anonymous=1)
#        print >>debug, "anonymous_reference", nodes, msg
#        return strstart, nodes, strend, msg



# 
