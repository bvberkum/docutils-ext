"""
Builders are preconfigured sets of Reader, Parser and Writer components.
"""
import logging
import docutils.core
import dotmpe
from dotmpe.du import comp


class Builder:

    Reader = comp.get_reader_class('standalone')
    Parser = comp.get_parser_class('restructuredtext')
    #Writer = comp.get_writer_class('xml')
    default_writer = 'pseudoxml'

    settings_overrides = {
        # do not read local files:
        'file_insertion_enabled': False,
        'embed_stylesheet': False,
        '_disable_config': True,
        # if the builder uses the html4css1 writer it needs this file:
        #'template': 'template.txt'
    }

    def __init__(self):
        # collect overrides for instance from inheritance chain:
        self.settings_overrides = get_overrides(self.__class__)
        parts = {}

    def build(self, source, source_id, settings_overrides):
        output, pub = self.__publish(source, source_id, None,
                settings_overrides)
        return pub.document, pub.source.successful_encoding

#        script = ''
#        for path in settings_overrides['javascript_paths']:
#            script += "<script type=\"application/javascript\" src=\"%s\"></script>" % path
#        # TODO: move this to XHTML writer if possible
#        parts['head'] += script
#        #import pprint
#        #print pprint.pformat(parts.keys())
#        for p in ['whole',]:
#            parts[p] = parts[p].replace('</head>', script+'\n</head>')

    def render(self, source, source_id, writer_name='html4css1',
            parts=['whole'], settings_overrides={}):
        writer_name = writer_name or self.default_writer
        writer = comp.get_writer_class(writer_name)()
        output, pub = self.__publish(source, source_id, writer,
                settings_overrides)
        self.parts = pub.parts
        return ''.join([pub.parts.get(part) for part in parts])

    def render_fragment(self, source, source_id, settings_overrides):
        return self.render(source, source_id, writer_name='html4css1',
                parts=['html_title', 'body'],
                settings_overrides=settings_overrides)

    # HTML-writer parts:                                                         #
    ['subtitle', 'version', 'encoding', 'html_prolog', 'header', 'meta',
     'html_title', 'title', 'stylesheet', 'html_subtitle',
     'html_body', 'body', 'head', 'body_suffix', 'fragment',
     'docinfo', 'html_head', 'head_prefix', 'body_prefix', 'footer',
     'body_pre_docinfo', 'whole']

    def __publish(self, source, source_path, writer, settings_overrides):
        source_class = None
        if isinstance(source, docutils.nodes.document):
            source_class = docutils.io.DocTreeInput
            parser = comp.get_parser_class('null')()
            reader = comp.get_reader_class('doctree')()
        else:
            source_class = docutils.io.StringInput 
            reader = self.Reader()
            parser = self.Parser()
        if not writer:
            writer = comp.get_writer_class('null')()
        destination_class = docutils.io.StringOutput
        overrides = self.settings_overrides
        overrides.update(settings_overrides)
        output, pub = docutils.core.publish_programmatically(
            source_class, source, source_path, 
            destination_class, None, None,
            reader, None,
            parser, None,
            writer, None,
            None, None,
            overrides, None, None)
        return output, pub


def get_overrides(klass, **settings):
    "Walk inheritance chain top down, updating settings with found overrides. "
    "FIXME: rewrite single level update to tree merge. "
    c = klass
    bases = [c]
    while c != Builder:
        c = c.__bases__[0]
        bases.append(c)
    while bases:
        c = bases.pop()
        settings.update(c.settings_overrides)
    return settings


