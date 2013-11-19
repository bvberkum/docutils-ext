from dotmpe.du import comp


# register all local modules with tag 'mpe' as Writer type
comp.register_extension_components(__name__, 'mpe', 'Writer', __file__)

