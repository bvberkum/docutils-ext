from dotmpe.du import comp

from inliner import Inliner


# register all local modules with tag 'mpe' as Parser type
comp.register_extension_components(__name__, 'mpe', 'Parser', __file__)
