Transforms
----------
:generator: xfoooooo

include.Include 
    Insert pieces of raw, unparsed content into the tree.
template.TemplateSubstitutions
    A variant on docutil's references.Substitutions. Formats a substitution
    value for a set of substitution references.
generate.PathBreadcrumb
    A substitution that inserts a 'breadcrumb'. A list of links generated from a
    path. The the source content path is used by default, and inserted into the
    header if the substitution reference is not present.
generate.Generated
    A more flexible way of including a timestamp based on substitution.
generate.SourceLink
    A more flexible way of including a sourcelink based on substitution.


.. important::
   
   While running extractors or other transforms that should work on original
   data, it may be necessary to move all generate transforms to run after the
   extractors, and do a second substitution round.


.. .. remote-include:: http://docutils.sourceforge.net/docs/ref/transforms.txt
   :cache: doc/du-transforms.rst

These are docutils standard transforms.

.. include:: doc/du-transforms.tmp.rst
   :start-line: 24
   :end-line: 95

See `Docutils Transforms`__ for more info on the priority values.       

==============================  ============================  ========
Transform: module.Class         Added By                      Priority
==============================  ============================  ========
spec.SpecInfo                   spec (r)                       20
include.Include                 mpe (r)                       180  
template.TemplateSubstitutions  mpe (r)                       190 
generate.PathBreadcrumb         mpe (r)                       200
generate.Generated              mpe (r)                       200
generate.CCLicenseLink          mpe (r)                       200
generate.SourceLink             mpe (r)                       200
==============================  ============================  ========


.. include:: doc/du-transforms.tmp.rst
   :start-line: 95
   :end-line: 103

.. __: transform priorities

