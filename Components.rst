Components
==========

.. _rST forms spec:

rST Forms
  dotmpe.du.form
    Formfield
      ..
    FormProcessor
      ..
    AbstractFormVisitor
      ..
    FormFieldSetVisitor
      ..
    FormFieldIDVisitor
      ..

  dotmpe.du.ext.transform.form1
    DuForm
      Initialize form processor, process all fields and run validator.
    GenerateForm
      Insert generated form (and values) into existing Du document.

  dotmpe.du.ext.extractor.form2
    FormExtractor
      Check form1 xform was valid. Store results with Nabu storage.

  dotmpe.du.ext.writer.formresults
    CSV writer for documents with ``form-processor``.


