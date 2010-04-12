from docutils import transforms, nodes


class SpecInfo(transforms.Transform):

#    default_priority = 

#    spec_names = 

    def apply(self):
        #if not getattr(self.document.settings, 'docinfo_xform', 1):
        #    return
        document = self.document
        index = document.first_child_not_matching_class(
              nodes.PreBibliographic)
        if index is None:
            return
        candidate = document[index]
        if isinstance(candidate, nodes.field_list):
            biblioindex = document.first_child_not_matching_class(
                  (nodes.Titular, nodes.Decorative))
            nodelist = self.extract_bibliographic(candidate)
            del document[index]         # untransformed field list (candidate)
            document[biblioindex:biblioindex] = nodelist



