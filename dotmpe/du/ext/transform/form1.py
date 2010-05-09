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

    form_spec = {}

    def apply(self):
        logging.info('DuForm.apply')
        settings = self.document.settings
        specs = self.form_spec or getattr(settings, 'form_spec', {})
        fp = form.FormProcessor(self.document, specs)
        fp.process_fields()
        setattr(settings, 'form_values', fp.values)
        fp.validate()


class FormTransform:
    
    """
    Recreate a Du document from a previously extracted form.
    """

