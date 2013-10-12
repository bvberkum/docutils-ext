from dotmpe.du import comp


# register all local modules with tag 'mpe' as Reader type
comp.register_extension_components(__name__, 'mpe', 'Reader', __file__)
