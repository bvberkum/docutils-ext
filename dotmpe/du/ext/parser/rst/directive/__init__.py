from docutils.parsers.rst import directives


directives._directive_registry.update({
        'include': ('dotmpe.du.ext.parser.rst.directives.blinc', 'Include'),
        'raw': ('dotmpe.du.ext.parser.rst.directives.blinc', 'Raw'),
        #'replace': ('dotmpe.du.ext.parser.rst.directives.blinc', 'Replace'),
    })
