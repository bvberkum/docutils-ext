Transforms
----------

.. 1 ---- 8< -----

``dotmpe.du.ext.transform.``
  ``clean.``
    `StripSubstitutionDefs`
      | ``--strip-substitution-definitions``
    `StripAnonymousTargets`
      | ``--strip-anonymous-targets``
  ``debug.``
    `Settings`
      Append document settings to document as a field-list
      (``--expose-settings``).
    `Options`  
      Append all publisher options to document as an option-list
      (``--expose-specs``).
  ``form1.``\ 
    `DuForm` 
      See ``dotmpe.du.form``.
    `GenerateForm` 
      Append a (filled) form to a document given a `fields_spec`.
    `FormMessages` 
      TODO: docs.
  ``generate.``\
    `Generator`
      Abstract ``include.Include`` for document content generators.
    `PathBreadcrumb`
      Insert linked 'breadcrumb' path at location.
      The breadcrumb is a list of links, generated from a path. 
      Works as a `TemplateSubstitution`.

      | ``--breadcrumb``
      | ``--no-breadcrumb``
      | ``--breadcrumb-path=PATH``
      | ``--breadcrumb-location=DECORATOR_OR_XPATH``
      | ``--breadcrumb-substitution-reference=REFNAME``
    `CCLicenseLink`
      TODO: docs.
      Works as a `TemplateSubstitution`.

      | ``--cc``
    `Timestamp`  
      A more flexible way of including a timestamp based on substitution.
    `SourceLink`
      A more flexible way of including a sourcelink based on substitution.
  ``include.``\ `Include`
      Insert raw data at location (``--include=XPATH,IDX,DATA|file:..``).
  ``template.``\ `TemplateSubstitution` 
      | ``--template-definitions``
      | ``--template-definition=REF[,TYPE,TRIML,TRIMR],DATA]``
      | ``--template-fields=NAME,..``

      A variant on docutil's references.Substitution. 
      Formats a substitution value for a set of substitution references.
  ``user.``\ `UserSettings` 
      | ``--user-settings=NAME,..``
      | ``--strip-user-settings``, ``--strip-settings``
      | ``--leave-user-settings``, ``--leave-settings``
      | ``--strip-settings-names=NAME,..``

      Override document settings by user data.

      If allowed for two publisher phases, or when this transform runs early
      enough, specific document settings can be overridden by values parsed from 
      the document.

.. 1 ---- >8 -----


.. important::
   
   While running extractors or other transforms that should work on original
   data, it may be necessary to move all generate transforms to run after the
   extractors, and do a second substitution round.


These two tables list the extension transforms and the docutils standard transforms by package and priority.
See `Docutils Transforms`__ for more info on the priority values.       

==============================  ============================  ========
Transform: module.Class         Added By                      Priority
==============================  ============================  ========
spec.SpecInfo                   spec (r)                       20
include.Include                 mpe (r)                       180  
template.TemplateSubstitution   mpe (r)                       190 
generate.PathBreadcrumb         mpe (r)                       200
generate.Generated              mpe (r)                       200
generate.CCLicenseLink          mpe (r)                       200
generate.SourceLink             mpe (r)                       200
clean.StripAnonymousTargets     mpe (r)                       900
clean.StripSubstitutionDefs     mpe (r)                       900
==============================  ============================  ========

.. .. remote-include:: http://docutils.sourceforge.net/docs/ref/transforms.txt
   :cache: doc/du-transforms.rst

.. include std xforms

.. include:: du-transforms,cache.rst
   :start-line: 23
   :end-line: 95

.. include table indicator legend

.. include:: du-transforms,cache.rst
   :start-line: 95
   :end-line: 103

.. __: transform priorities

