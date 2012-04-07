
#try:
#    import pkg_resources
#    pkg_resources.declare_namespace(__name__)
#except ImportError:
## don't prevent use of paste if pkg_resources isn't installed
#    from pkgutil import extend_path
#    __path__ = extend_path(__path__, __name__)
#
#try:
#    import modulefinder
#except ImportError:
#    pass
#else:
#    for p in __path__:
#        modulefinder.AddPackagePath(__name__, p)
#    del p


import docutils

# 0.7
# 0.8
#
#du_version = map(int,docutils.__version__.split('.'))
#if (du_version[0] != 0 or (du_version[0] == 0 and du_version[1] != 8)):
#    raise Exception("Unkown version: "+docutils.__version__)

import comp
#import flatten
#import form
#import frontend
import ext

