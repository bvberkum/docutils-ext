"""
Builders are preconfigured sets of Reader, Parser and Writer components.
"""
import docutils.core
import dotmpe
from dotmpe.du import comp


class Builder:

    Reader = comp.get_reader_class('standalone')
    Parser = comp.get_parser_class('restructuredtext')
    #Writer = comp.get_writer_class('xml')
    default_writer = 'pseudoxml'

    settings_overrides = {
        '_disable_config': True,
        'file_insertion_enabled': False,
        'embed_stylesheet': False,
        'spec_names': ['build'],
        'strip_spec_names': ['build'],
    }

    def __init__(self):
        self.settings_overrides = get_overrides(self.__class__)

    def build(self, *args, **kwds):
        parts = self.build_parts(*args, **kwds)
        return parts['whole']            

    def build_fragment(self, *args, **kwds):
        parts = self.build_parts(*args, **kwds)
        return parts['html_title'] + parts['body']

    def build_parts(self, source, source_id, writer, **settings_overrides):
        # settings are assumed to be valid!
        writer_name = writer or self.default_writer
        overrides = self.settings_overrides
        overrides.update(settings_overrides)
        parts = docutils.core.publish_parts(
                source=source, source_path=source_id,
                reader=self.Reader(),
                parser=self.Parser(),
                #writer_name=writer_name,
                writer=comp.get_writer_class(writer_name)(),
                settings_overrides=overrides)

#        script = ''
#        for path in settings_overrides['javascript_paths']:
#            script += "<script type=\"application/javascript\" src=\"%s\"></script>" % path
#        # TODO: move this to XHTML writer if possible
#        parts['head'] += script
#        #import pprint
#        #print pprint.pformat(parts.keys())
#        for p in ['whole',]:
#            parts[p] = parts[p].replace('</head>', script+'\n</head>')

        return parts


def get_overrides(klass, **settings):
    "Walk inheritance chain top down, updating settings with found overrides. "
    c = klass
    bases = [c]
    while c != Builder:
        c = c.__bases__[0]
        bases.append(c)
    while bases:
        c = bases.pop()
        settings.update(c.settings_overrides)
    return settings


