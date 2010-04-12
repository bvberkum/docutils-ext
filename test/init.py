import sys, os, glob

# allow import of dotmpe
PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
PROJ_LIB = os.path.join(PROJ_ROOT, 'lib')
sys.path.insert(0, PROJ_LIB)

# list some resources for testing
README = os.path.join(PROJ_ROOT, 'README.rst')

TEST_DOC = glob.glob(os.path.join(PROJ_ROOT, 'var', '*.rst'))
TEST_DOC.sort()

# XXX: have a look at lossless-rst-writer branch
print os.path.join(PROJ_LIB, 'docutils-branches',
	'lossless-rst-writer', 'docutils', 'writers')
sys.path.insert(0, os.path.join(PROJ_LIB, 'docutils-branches',
	'lossless-rst-writer', 'docutils', 'writers'))
# access extension module directly
LOSSLESS_WRITER = __import__('rst') 