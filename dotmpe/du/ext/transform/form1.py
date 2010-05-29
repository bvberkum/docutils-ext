"""
form1 - Du transform components for dotmpe.du.form.
"""
import logging
from docutils import transforms, nodes
from dotmpe.du import form


logger = logging.getLogger(__name__)

class DuForm(transforms.Transform):

    """
    See dotmpe.du.form for documentation.

    Depending on settings, this parses and validates user data from certain
    fields in the document. 

    In particular, a FormProcessor is (re)initialized for the document with a
    fields_spec list taken from this class or provided through command-line
    options.
    """

    default_priority = 520

    # See dotmpe.du.form for settings_spec

    fields_spec = []

    def apply(self):
        doc = self.document
        settings = self.document.settings
        if not hasattr(settings, 'form') or settings.form == 'off':
            return
        fp = form.FormProcessor.get_instance(self.document, self.fields_spec)
        #logging.info(self.document.pformat())
        form_process = getattr(settings, 'form_process', 'validate')
        if form_process == 'prepare':
            logging.info('DuForm preparing %r. ', doc['source'])
            fp.process_fields(False)
        elif form_process != 'submit': # invoke validation here or in extrctr..
            logging.info('DuForm validating %r. ', doc['source'])
            fp.process_fields()
            valid = fp.validate()
            #if not valid:
            #    self.document.reporter.error( 'Form has errors. ',)
            #else:                
            #    self.document.reporter.debug( 'Form is valid. ',)
        #logging.info(self.document.pformat())


class GenerateForm(transforms.Transform):
    
    """
    Recreate or generate a form in an existing Du document, fill-in values if available.
    Best used in writer-phase.
    """

    default_priority = 500

    fields_spec = []

    def apply(self):
        settings = self.document.settings
        if not hasattr(settings, 'form_generate') or \
                'off' in settings.form_generate:
            return
        fp = form.FormProcessor.get_instance(self.document, self.fields_spec)
        if not fp.nodes:
            logging.info('GenerateForm: preparing form. ')
            fp.process_fields(False)
        # Generate missing fields
        values = getattr(settings, 'form_values', {})
        logging.info('Generating missing fields for %s', settings.form_generate)
        for field_id, field in fp.iter_missing(*settings.form_generate):
            if field_id in values:
                fp[field_id] = values[field_id]
            else:
                fp[field_id] = u''


class FormMessages(transforms.Transform):

    """
    Normally, universals.Messages runs to take any transformer message for the 
    document and insert these into an appendix section of the class 'system-messages'.

    ``document.transform_messages`` is afterward left empty.
    """

    default_priority = 855

    def apply(self):
        if self.document.form_processor.messages:
            messages = nodes.section()
            messages += nodes.title('','Form messages')
            messages += self.document.form_processor.messages
            self.document += messages
            self.document.form_processor.messages[:] = []

