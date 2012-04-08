from dotmpe.du import comp

from inliner import Inliner


comp.register_extension_components(__name__, 'mpe', 'Parser', __file__, 
        ['inliner'])
