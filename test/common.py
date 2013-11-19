"""
"""
import init
from util import mkclassname, new_writer_testcase
from rstwriter import create_lossy_pxml_compare_tests, create_lossess_compare_tests


def create_tests():
    create_lossy_pxml_compare_tests('rst-mpe', init.RST_COMMON)
    #create_lossess_compare_tests(init.RST_COMMON)

