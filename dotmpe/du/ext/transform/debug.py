import logging, optparse
from docutils import transforms, nodes, frontend
from dotmpe.du.comp import get_builder_class



class Settings(transforms.Transform):
    " Write settings to field-list in document. "

    default_priority = 500

    settings_spec = (
                ('Expose current settings in field-list. ', 
                    ['--expose-settings'],
                    {'action':'store_true','default':False}
                ),
        )

    def apply(self):
        settings = self.document.settings
        if not getattr(settings, 'expose_settings', 0):
            return
        logging.debug("DEBUG: Writing settings field-list to document. ")
        field_list = nodes.field_list()
        for setting in dir(settings):
            if setting.startswith('_'): continue
            value = getattr(settings, setting)
            if callable(value):
                value = value.__module__ +':'+ value.__name__ +'()'
            field = nodes.field('',*[
                    nodes.field_name('',setting),
                    nodes.field_body('',*[
                        nodes.paragraph('',*[ nodes.Text(str(value)) ])
                    ])
                ])
            field_list += field
        self.document += nodes.section('',*[
                nodes.title('','Docutils settings'),
                 field_list
            ])            

class Options(transforms.Transform):
    """ This loads the (Re?)Reader, Parser and Writer for current builder and writes
    option-lists to the document.
    """

    default_priority = 500

    settings_spec = (
            ('Expose SettingsSpecs for builder in option-lists. ', 
            ['--expose-specs'],
            {'action':'store_true', 'default':False}),
            # --classes : Reader, Parser, Writer
        )

    def apply(self):
        settings = self.document.settings
        if not getattr(settings, 'expose_specs', 0):
            return
        buildername = getattr(settings, 'build', None)
        if not buildername:
            self.document.reporter.error("Cannot apply debug.Options transform "
                    "without `build` setting.  ")
            return

        self.__expose_options(buildername)

    def __expose_options(self, buildername):
        """
        Add a section to the document containing an optiongroup with options
        provided by the builder/reader/parser combo.
        """
        p = buildername.rfind('.')
        assert p>-1, "Illegal build-line: %s" % buildername
        package_name, class_name = buildername[:p], buildername[p+1:]
        builder_class = get_builder_class( package_name, class_name )
        prsr = frontend.OptionParser(components=(
                builder_class.Reader, builder_class.Parser, #builder_class.Writer
            ))

        specnode = nodes.section('',nodes.title('','Docutils Options'))
        specnode += self.__add_optiongroup(prsr)
        for optiongroup in prsr.option_groups:
            specnode += nodes.title('', optiongroup.title)
            specnode += self.__add_optiongroup(optiongroup)

        self.document += specnode

    def __add_optiongroup(self, opts):
        if not opts.option_list:
            return ''
        option_list = nodes.option_list()
        for option in opts.option_list:
            option_list += self.__add_option(option)
        return option_list

    def __add_option(self, option):
        if option.action not in ('callback','store_const','store_true',
                'store_false','count','version','help'):
            optnodes = [ nodes.option('', nodes.option_string('',o),
                nodes.option_argument('', option.metavar or 'ARG'))
                for o in option._short_opts + option._long_opts ]
        else:                
            optnodes = [ nodes.option('', nodes.option_string('',o),)
                for o in option._short_opts + option._long_opts ]

        help =  u''                
        if option.help != optparse.SUPPRESS_HELP:
            if option.default != optparse.NO_DEFAULT:
                help = option.help.replace('%default', str(option.default))
            else:                
                help = option.help
        item = nodes.option_list_item('',
                nodes.option_group('', *optnodes))
        if help:
            item += nodes.description('',nodes.paragraph('',help))
        return item


