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

    settings_spec = (
        )

    def apply(self):
        logging.info('DuForm.apply')
        fp = form.FormProcessor(self.document)
        fp.process_fields()
        fp.validate()
        #if fp.errors:
        #fp.report_form_errors()


class FormTransform:
    
    """
    Recreate a Du document from a previously extracted form.
    """

