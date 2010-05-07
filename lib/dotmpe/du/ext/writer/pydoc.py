"""
A would-be python doc writer.
This is nowhere near finished. Duck-tape and moving parts follow, keep clear ;)
"""
from docutils import nodes
from docutils.writers import html4css1


class HTMLTranslator(html4css1.HTMLTranslator):

    # XXX: Python Source Reader support

    #  Structural Elements

    def visit_module_section(self, node):
        self.body.append(self.starttag(node, 'div'))
    def depart_module_section(self, node):
        self.body.append('</div>')

    def visit_class_section(self, node):
        self.body.append(self.starttag(node, 'div'))
    def depart_class_section(self, node):
        self.body.append('</div>')

    def visit_class_base(self, node): pass
    def depart_class_base(self, node): pass
    def visit_method_section(self, node): pass
    def depart_method_section(self, node): pass
    def visit_attribute(self, node): pass
    def depart_attribute(self, node): pass
    def visit_function_section(self, node): pass
    def depart_function_section(self, node): pass
    def visit_class_attribute_section(self, node): pass
    def depart_class_attribute_section(self, node): pass
    def visit_class_attribute(self, node): pass
    def depart_class_attribute(self, node): pass
    def visit_expression_value(self, node): pass
    def depart_expression_value(self, node): pass
    def visit_attribute(self, node): pass
    def depart_attribute(self, node): pass

    # Structural Support Elements

    def visit_parameter_list(self, node): pass
    def visit_parameter_tuple(self, node): pass
    def visit_parameter_default(self, node): pass
    def visit_import_group(self, node): pass
    def visit_import_from(self, node): pass
    def visit_import_name(self, node): pass
    def visit_import_alias(self, node): pass
    def visit_docstring(self, node): pass

    #  Inline Elements

    def visit_object_name(self, node): pass
    def visit_parameter_list(self, node): pass
    def visit_parameter(self, node): pass
    def visit_parameter_default(self, node): pass
    def visit_class_attribute(self, node): pass
    def visit_attribute_tuple(self, node): pass


    # Structural Support Elements

    def depart_parameter_list(self, node): pass
    def depart_parameter_tuple(self, node): pass
    def depart_parameter_default(self, node): pass
    def depart_import_group(self, node): pass
    def depart_import_from(self, node): pass
    def depart_import_name(self, node): pass
    def depart_import_alias(self, node): pass
    def depart_docstring(self, node): pass

    #  Inline Elements

    def depart_object_name(self, node): pass
    def depart_parameter_list(self, node): pass
    def depart_parameter(self, node): pass
    def depart_parameter_default(self, node): pass
    def depart_class_attribute(self, node): pass
    def depart_attribute_tuple(self, node): pass

