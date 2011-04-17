import sys, os, glob


# add dotmpe to import path
PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
PROJ_LIB = os.path.join(PROJ_ROOT, 'lib')
sys.path.insert(0, PROJ_LIB)

# list some resources for testing
README = os.path.join(PROJ_ROOT, 'README.rst')

TEST_DOC = filter(os.path.getsize,
        glob.glob(os.path.join(PROJ_ROOT, 'var', 'test-*.rst'))
#            +
#        glob.glob(os.path.join('/srv', 'htdocs-mpe', 'note', '*.rst'))
    )
TEST_DOC.sort()



# XXX: have a look at lossless-rst-writer branch
#print os.path.join(PROJ_LIB, 'docutils-branches',
#	'lossless-rst-writer', 'docutils', 'writers')
sys.path.insert(0, os.path.join(PROJ_LIB, 'docutils-branches',
	'lossless-rst-writer', 'docutils', 'writers'))
# access extension module directly
LOSSLESS_WRITER = __import__('rst') 
