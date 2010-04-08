import sys, os, glob

PROJ_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJ_ROOT, 'lib'))

README = os.path.join(PROJ_ROOT, 'README.rst')

TEST_DOC = glob.glob(os.path.join(PROJ_ROOT, 'var', '*.rst'))
