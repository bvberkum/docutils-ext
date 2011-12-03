"""
Registry of component names, for lazy loading, caching, and more flexible (and
insecure) module import.
"""
import logging
import glob
import os
import sys

import docutils


logger = logging.getLogger(__name__)


def load_module(module_path):

    """
    Import the module indicated by `module_path`.
    """

    p = module_path.rfind('.')+1
    super_module = module_path[p:]
    try:
        module = __import__(module_path, fromlist=[super_module], level=0)
        return module    
    except ImportError, e:
        logger.critical('Failed importing module %s from %s.  ',
                super_module, module_path)
        raise e


def component_loader(component_type):
    """
    Create a `get_<component_type>_class` function for `component_type`.
    """
    component_type = component_type.lower()
    component_group = component_type + 's'
    ext_component_aliases = getattr(sys.modules[__name__], component_group)
    ext_component_modules = getattr(sys.modules[__name__], '_'+component_group)
    def get_component_class(component_alias, klass=component_type.title()):
        "Import `klass` from the module registered with `%s_name`." % component_type
        if component_alias not in ext_component_modules:
            #print "Loading %s_name" % component_type, component_alias, klass
            if component_alias in ext_component_aliases:
                ext_component_module = ext_component_aliases[component_alias]
                ext_component_modules[component_alias] = load_module(ext_component_module)
            else:
                assert klass == component_type.title(), \
                        "Du `get_%s_class` can only load %s component classes named '%s'." \
                                % (component_type, component_group, component_type.title())
                du_component_loader = getattr(
                        getattr(docutils, component_group), 
                        "get_%s_class" % component_type)
                return du_component_loader(component_alias)
        return getattr(ext_component_modules[component_alias], klass)
    return get_component_class


readers = {}
"Alias, module mapping. "
_readers = {}
"Class object cache. "

get_reader_class = component_loader('Reader')

#def get_reader_class(reader_name, klass='Reader'):
#    if reader_name not in _readers:
#        reader_mod = reader_name
#        if reader_mod in readers:
#            reader_mod = readers[reader_mod]
#            _readers[reader_name] = load_module(reader_mod)
#        else:
#            assert klass == 'Reader'
#            return docutils.readers.get_reader_class(reader_name)
#    return getattr(_readers[reader_name], klass)


parsers = {}
"Alias, module mapping. "
_parsers = {}
"Class object cache. "

get_parser_class = component_loader('Parser')


writers = {}
"Alias, module mapping. "
_writers = {}
"Class object cache. "

get_writer_class = component_loader('Writer')

                

ERR_MISSING_BUILDER_MODNAME = "Missing builder module name. "

builders = { }

def get_builder_class(mod_name, class_name='Builder'):
    global builders
    assert mod_name, ERR_MISSING_BUILDER_MODNAME
    #if not class_name or (restrict and class_name not in restrict):
    #    class_name = 'Builder'
    if mod_name not in builders:
        logger.debug("Loading builder package %s ", mod_name)
        module = load_module(mod_name)
        builders[mod_name] = module
    else:
        module = builders[mod_name]
    return getattr(module, class_name)


ERR_MISSING_EXTRACTOR_MODNAME = "Missing extractor module name. "

extractors = { }

def get_extractor_class(mod_name, class_name='Extractor'):
    global extractors
    assert mod_name, ERR_MISSING_EXTRACTOR_MODNAME
    #if not class_name or (restrict and class_name not in restrict):
    #    class_name = 'Extractor'
    if mod_name not in extractors:
        logger.debug("Loading extractor package %s ", mod_name)
        module = load_module(mod_name)
        extractors[mod_name] = module
    else:
        module = extractors[mod_name]
    return getattr(module, class_name)


ERR_MISSING_EXTRACTOR_STORAGE_MODNAME = "Missing extractor_storage module name. "

extractor_storages = { }

def get_extractor_storage_class(mod_name, class_name='Storage'):
    global extractor_storages
    assert mod_name, ERR_MISSING_EXTRACTOR_STORAGE_MODNAME
    #if not class_name or (restrict and class_name not in restrict):
    #    class_name = 'Storage'
    if mod_name not in extractor_storages:
        logger.debug("Loading extractor_storage package %s ", mod_name)
        module = load_module(mod_name)
        extractor_storages[mod_name] = module
    else:
        module = extractor_storages[mod_name]
    return getattr(module, class_name)


def get_extractor_pair(mod_name):
    return get_extractor_class(mod_name), get_extractor_storage_class(mod_name)


## Util

def register_extension_components(ext_module_prefix, ext_tag, ext_type, ext_dir):

    """
    Helper function to register all submodules in `ext_module_prefix` (at
    system directory `ext_dir`) as `ext_type` components. This type is either
    'Reader', 'Writer' or 'Parser'. Each submodule's filename is used as the
    alias, but only if the alias is not a known component of this `ext_type` to 
    standard docutils. The extension is always aliased using `ext_tag` as a
    suffix (separated by '-').

    Ie., custom Writer component 'html' with `ext_tag` 'test' registers under alias 
    'html-test', but not 'html' since it already exists. On the other hand 'rst'
    aliases to both 'rst' and 'rst-test'.
    """

    if (os.path.isfile(ext_dir)):
        ext_dir = os.path.dirname(ext_dir)

    du_comp_mod = getattr(docutils, ext_type.lower()+'s')
    du_comp_reg = getattr(du_comp_mod, "_%s_aliases" % ext_type.lower())
    
    du_ext_comp_reg = getattr(sys.modules[__name__], ext_type.lower()+'s')

    ext_names = \
        map(lambda x:x.split('.')[0],
            map(
                os.path.basename,
                glob.glob(os.path.join(ext_dir, '[!_]*.py'))))

    for ext_name in ext_names:
        ext_module = ext_module_prefix + '.' + ext_name
        tagged_name = ext_name +'-'+ ext_tag

        # register name with ``dotmpe.du.comp``
        if ext_name not in du_comp_reg:
            du_ext_comp_reg[ext_name] = ext_module
        du_ext_comp_reg[tagged_name] = ext_module

