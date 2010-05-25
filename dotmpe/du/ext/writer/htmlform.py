import logging
from docutils import nodes
from dotmpe.du.ext.writer import html


class HTMLTranslator(html.HTMLTranslator):

    def __init__(self, document):
        html.HTMLTranslator.__init__(self, document)
        settings = document.settings
        self.form_field = None # current visit is outlined by..
        self.form_class = getattr(settings, 'form_class', 'form')
        self.has_form = getattr(settings, 'form_fields_spec', None) != None
   
    def visit_document(self, node):
        if self.has_form:
            self.body.append("<form action=\"%s\" method=\"POST\" >" %
                    self.document['source'])
        html.HTMLTranslator.visit_document(self, node)            

    def depart_document(self, node):
        if self.has_form:
            self.body_pre_docinfo.append("<p><input type=\"submit\"/></p>")
            self.body.append("<p><input type=\"submit\"/></p>")
            self.body.append("</form>")
        html.HTMLTranslator.depart_document(self, node)            

    def visit_field(self, node):
        if self.form_class+'-field' in node['classes']:
            self.form_field = nodes.make_id(node[0].astext())
        html.HTMLTranslator.visit_field(self, node)            

    def depart_field(self, node):
        if self.form_field:
            assert self.form_field == nodes.make_id(node[0].astext())
            self.form_field = None
        html.HTMLTranslator.depart_field(self, node)            

    def visit_field_body(self, node):
        html.HTMLTranslator.visit_field_body(self, node)            
        if self.form_field:# TODO move ID=self.form_field to field-node
            self.body.append('<p>'+self.starttag(node, 'input', value=node.astext(),
                type='text', Class='', name=self.form_field ))
            self.body.append('</input></p>')

    def depart_field_body(self, node):
        html.HTMLTranslator.depart_field_body(self, node)            


class Writer(html.Writer):

    def __init__(self):
        html.Writer.__init__(self)
        self.translator_class = HTMLTranslator


