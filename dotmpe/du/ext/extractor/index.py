"""
2010-04-22 - An would-be 'indexer' for hierarchically structured document(s).
This is nowhere near finished. Duck-tape and moving parts follow, keep clear ;)

- Each section, title or term is scanned for a name.
  An reference target for this node is generated and noted in the storage.

- Each title reference is scanned for a known name, and an index entry is made
  if a known target is referenced. Optionally the title element is converted for
  the first or all occurence in a document. Ie. a numbered list of cross-links
  is added, or the title replaced itself by another reference.

- Each normal named reference will ofcourse have its target available in the
  same or another document. The target is added if needed.

- The stored data can be used to generate an index, a sorted list of names and
  references to their original occurences.

several options are made
  available to rewrite the reference.


"""
from nabu import extract


class IndexRegistryExtractor(extract.Extractor):

    """
    Extract named index items from multiple documents, and gather references to those
    names. Multiple registries possible but default to 'Index'.

    Named Registry of Indices for Named Items.
    """

    settings_spec = ((
            'Append or reset the list of elements scanned for new targets. ',
            ['--index-targets'],
            {'default':['document','section','term'],'action':'append',
                'metavar':'[REGNAME:]ELEMENT[,]'}
        ),(
            'Set the default registry. ',
            ['--index-default-registry'],
            {'default':'Index'}
        ),(
            'Append or reset the list of inline elements scanned for aditional '
            'references. '
            'By default accepts the internal nodes `reference` and `title-reference`. ',
            ['--indexed-references'],
            {'default':['reference', 'title-reference']}
        ),(
            'Set the behaviour upon finding multiple index item definitions. '
            'Note that on append, the *primary target* and target ordering of '
            'the item depends on the order of ``--index-targets`` and the '
            "(outer-)document ordering. A value of 'keep' or 'redefine' either "
            "ignores all but the first or last respectively. ",
            ['--index-duplicates'],
            {'choice': ('error','keep','redefine','append')}
        ),(
            'Set the rewrite behaviour on matching title references, does nothing '
            'but extract data by default (``index``). '
            'This does not affect the type of the reference kept in the storage. '
            'Multiple options may be present but index is always implied. '
            'The following are two mutually '
            'exclusive groups of alternative options. '
"""

- ``primary-link`` causes the element to be rewritten to refer to the
  *primary target*. If the matched element was a reference this obviously
  replaces semantics, quite likely generalizing it.
- ``link`` varies from primary-link in that it only rewrite non-reference
  elements.

- ``append-cross-link`` appends numbered links to each occurrence,
- ``append-index-link`` links to the entry in the index registry document using
  a symolic footnote?
  document must be generated at `path/index.rst`?
""",
            ['--index-reference-match'],
            {'choice':('leave','primary-link','link','append-index-link','append-cross-links',)}
        ),(
            'Like ``reference-match`` set the rewrite behaviour, but for the targets. '
            'This should allow embedding lots of extra navigational information. ',
            ['--index-target-match'],
            {'choice':('leave','append-index-link','append-cross-links',)}
        ))

    default_priority = 900

    def apply(self, unid=None, store=None, **kwargs):
        """
        This transform performs two traverse on the document.

        First the actual data extraction to find new names,
        secondly the tree is rewritten, inserting reference targets and
        rewriting inline structures.

        FIXME: Note that each new target invalidates all other build documents
        that reference that target, ie. mentioning the particular .
        """
        #settings = self.documents.settings

        for reg in self.settings.target_references:
            targets = settings.target_references.get(reg)
            for node in self.traverse(*targets):
                node

        for reg in self.settings.indexed_references:
            references = self.settings.indexed_references.get()
            for node in self.traverse(*references):
                if self.store:
                    node


class RegistryIndexGenerator(generate.Generator):
    """
    A regular transform to publish the datastore data.

    With the data in the store, it is possibly to generate several documents
    serving as cross indexes for use in e.g. manifests or appendices.

    Each generally consists of a list of name, references pairs.

    The source-id or UNID is opaque, but with breadcrumb there is an hierarchical
    relationship that establishes paths.
    That, at it's turn, is probably subsumed by subdocs.
    """

    def generate(self):
        pages = []
        for registry in ('Index',):
            page = nodes.Section('','',names=registry)
            page.append(nodes.title('',registry))

            for name in self.store.get(registry=registry):
                item = self.generate_index(registry, name)
                page.append(item)

            self.document.append(page)
            pages.append(page)
        return pages

    def generate_index(self, registry, name):
        index_item = nodes.list_item(names=name)
        index_item.append(nodes.inline('',name))

        for target in self.store.get(name, type=TARGET,
                registry=registry):
            ref = nodes.reference('','',len(ocurrences),
                    names=name)
            index_item.append(ref)

        for item in self.store.get(name, type=REFERENCE,
                registry=registry):
            ref = nodes.reference('','',len(ocurrences),
                    names=name)
            index_item.append(ref)

        return index_item


# Storage types

REFERENCE = 1
TARGET = 2

try:
    import google.appengine.ext

except ImportError, e:
    print globals()

finally:

    class Registry(db.Model):
        name = db.StringProperty()
    class IndexItem(db.Model):
        registry = db.ReferenceProperty(Registry)
        name = db.StringProperty()
    class IndexReference(db.Model):
        item = db.ReferenceProperty(IndexItem)
        source = db.StringProperty()
    class IndexTarget(db.Model):
        item = db.ReferenceProperty()
        source = db.StringProperty()

    class GAEIndexRegistryExtractorStorage(extract.ExtractorStorage):
        def store(self, source_id, name, type=REFERENCE, registry='Index'):
            pass
        def get(self, name=None, type=TARGET, registry='Index'):
            pass
        def clear(self, source_id, name=None, type=None, registry='Index'):
            pass
