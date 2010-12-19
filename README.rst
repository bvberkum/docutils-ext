docutils-ext.mpe
================
Extensions for Python docutils.
May need latest docutils from SVN.

Development targets
  - reST directives for left- and right-margin decoration.
  - An ``html4css1`` writer with margin support.
  - Testing experimental rst re-writer, see test/.
  - Additional document transforms and settings (``dotmpe.du.ext.transform``).

    ``clean.``\ `StripSubstitutionDefs`
      | ``--strip-substitution-definitions``
    ``clean``.\ `StripAnonymousTargets`
      | ``--strip-anonymous-targets``
    ``debug.``\ `Settings`
        Append document settings to document as a field-list
        (``--expose-settings``).
    ``debug.``\ `Options`  
        Append all publisher options to document as an option-list
        (``--expose-specs``).
    ``form1.``\ `DuForm` 
        See ``dotmpe.du.form``.
    ``form1.``\ `GenerateForm` 
        Append a (filled) form to a document given a `fields_spec`.
    ``form1.``\ `FormMessages` 
        TODO 
    ``generate.``\
      `Generator`
        Abstract ``include.Include``.
    ``generate.``\ `PathBreadcrumb`
        | ``--breadcrumb``
        | ``--no-breadcrumb``
        | ``--breadcrumb-path=PATH``
        | ``--breadcrumb-location=DECORATOR_OR_XPATH``
        | ``--breadcrumb-substitution-reference=REFNAME``

        Insert linked 'breadcrumb' path at location.
    ``generate.``\ `CCLicenseLink`
        | ``--cc``

        TODO: docs
    ``generate.``\ `Timestamp`  
        TODO: docs
    ``generate.``\ `SourceLink`
        TODO: docs
    ``include.``\ `Include`
      Insert raw data at location (``--include=XPATH,IDX,DATA|file:..``).
    ``template.``\ `TemplateSubstitutions` 
        | ``--template-definitions``
        | ``--template-definition=REF[,TYPE,TRIML,TRIMR],DATA]``
        | ``--template-fields=NAME,..``

        TODO: insert raw nodes at location.
    ``user.``\ `UserSettings` 
        | ``--user-settings=NAME,..``
        | ``--strip-user-settings``, ``--strip-settings``
        | ``--leave-user-settings``, ``--leave-settings``
        | ``--strip-settings-names=NAME,..``

        Override document settings by user data.

        If allowed for two publisher phases, or when this transform runs early
        enough, specific document settings can be overridden by values parsed from 
        the document.

  - These transforms are used by ``dotmpe.du.ext.reader.mpe.``\ `Reader`.
  - Several Nabu `Extractor`, `Storage` pairs (``dotmpe.du.ext.extractor``).

    ``form2.``\ `FormExtractor` and `FormStorage`
      TODO docs
    ``include.``\ `IncludeDoctree`
      TODO w.i.p.
    ``index.``\ `IndexRegistryExtractor`
      TODO w.i.p.
    ``inline.``\ `InlineExtractor`
      TODO w.i.p.
    ``reference.``\ `Extractor`
      TODO w.i.p.

  - ``dotmpe.du.form``\ `FormField`
  - ``dotmpe.du.builder`` has some packages with specific Reader/Parser/Writer
    component configurations, but frontend is undergoing work.

These are currently working and maintained.

To be completed
  - extractor/form framework
  - reST forms. TODO: docs. The ``dotmpe.du.form``\ `FormProcessor`, used in transforms (``form1``) and extractors (``form2``).
    Forms allow for ``fields_spec`` which is used on the document tree like ``settings_spec`` is on argv. 
    Enable validation, feedback and more structured definitions of extractors.
  - reST directives for breadcrumbs.
  - TODO: docs. An inliner for the reST parser ``dotmpe.du.ext.parser.inliner``.

Also in this project some `documentation on Du`__, and there are `some examples of reST and docutils`__ code.  
XXX: separate project? A first stab at a quick-reference chart for Du/reST, based in reST. See if combinable with sheet.



.. __: doc/main.rst  
.. __: examples

dotmpe extensions
-----------------

Directives
''''''''''
Left- and right-margin are decoration blocks like the page header and footer.
There is at most one of each per page.
::

  .. margin:: left
  
     Margin contents left-side.
  
  .. margin:: right
     :class: my-doc
     
     Margin contents right-side.
  
  .. margin:: left
  
     More contents left-side.

Transforms
''''''''''
Docutils includes setting specs for some of its transforms into core and
frontend. The ``dotmpe.du.ext.reader.mpe`` Reader replaces some of these 
transforms with implementations that provide their own flexible 
settings spec.

.. include:: doc/transforms.rst
   :start-line: 3
   :end-line: 18

.. start/end line requires du rev >= 6185

Read more about them in `Transforms <doc/transforms.rst>`__.


Overview
--------
Work in progress:

  - There is my own attempt at an rst writer, and in test/init.py the writer from
    Stefan's docutils branch is included. Not under active development but i hope to pick
    it up.

  - Before that happens I'm cleaning up code from some other docutils related projects.
    dotmpe.du.builder is shaping up nicely to be a collection of publishers for
    running in an server-environment. Maybe these can wrap some Nabu stuff
    (data-mining) later. Front-end development active in `Blue Lines`__.

.. __: http://blue-lines.appspot.com/

Other ToDo
  -  propose breadcrumb and other generate transforms on devel list
     Lea mentioned breadcrumbs.
  -  re-evaluate include, literal and raw dereferencing.
  -  ``--use-bibtex=USE_BIBTEX`` off latex2e may be nice practical example of external
     resource framework integration.
  -  directive options are not all i18n'd

What follows is some thoughts on document publishing.

Host-based publishing
----------------------
The standalone publisher works by deferring resource dereference to a host
system, i.e. the local filesystem. But

- there is no integrity checking,
- there is no explicit document base, or reconition of the document access
  protocol, and in short:
- there is no system for explicit document identification across protocols.

Standard Du works includes and stylesheets from files, and does not care what
references point to. 
The choice to only dereference local files is out of security consideration.

But here it misses conveniences that protocols can offer.
It does not at all register where content comes from, i.e. an include is evaluated
into a fully parsed document tree.
The document root that acts as an envelope, recording source and document id,
is discarded upon inclusion.
Also, multiple includes may create errors in case of ID's, e.g. `roles`
definitions collide.

.. XXX: see TODO 1


Examples
--------
- form demonstration
- example rSt on inline references and roles
- breakcrumbs

.. TODO: 

Log
-----
2010-11-04
  Stefan Merten published his xml2rst and included an installer.
  He also has rst2gxl 'producing GXL which can be transformed to dot'
  and rst2diff 'comparing two input files producing a marked up difference
  output'.
  See the `source directory <~/src/python-docutils>`__

2010-12-01
    Integrating figure label patch by Alex @ du mailinglist.
    Created subclass of latex2e writter for this.



