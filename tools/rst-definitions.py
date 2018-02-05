"""
:Created: 2015-07-27
:Updated: 2016-08-28

TODO: maybe a frontend with no writer, just recording transforms/extractors..
"""
from __future__ import print_function

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description, \
    publish_doctree, Publisher


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    if not args:
        args = [
                '/srv/project-local/script-mpe/test/pd-spec.rst',
                '/srv/project-local/script-mpe/test/finfo-spec.rst',
                '/srv/project-local/script-mpe/test/var/esop/1-simple-spec.rst'
            ]

    for fn in args:
        source = open(fn).read()

        doctree = publish_doctree(source, source_path=fn,
            reader=None, reader_name='standalone',
            parser=None, parser_name='restructuredtext',
            settings=None, settings_spec=None, settings_overrides=None, config_section=None,
            enable_exit_status=False)
        #print(doctree)
