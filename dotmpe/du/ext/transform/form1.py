"""
form1 - Du transform components for dotmpe.du.form.
"""
import logging
from docutils import transforms
from dotmpe.du import form



class DuForm(transforms.Transform):

    """
    See dotmpe.du.form for documentation.

    Depending on settings, this parses and validates user data from certain
    fields in the document. 
    """

    default_priority = 500

    # See dotmpe.du.form for settings_spec

    fields_spec = []

    def apply(self):
        if not hasattr(self.document, 'form_processor'):
            fp = form.FormProcessor(self.document)
        else:
            fp = self.document.form_processor
        if self.fields_spec:
            fp.initialize(self.document, self.fields_spec)
        fp.process_fields()
        fp.validate()

## Form generator

class GenerateForm(transforms.Transform):
    
    """
    Recreate or generate a Du document with previously initialized form.
    Populate with (default) data if present.
    """

    def apply(self):
        settings = self.document.settings
        specs = self.form_spec or getattr(settings, 'form_spec', {})
        values = getattr(settings, 'form_values', {})
        #for field_id in 



