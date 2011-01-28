
if __name__ == '__main__':
    import os
    import init
    import docutils.core
    for doc in init.TEST_DOC:
        print (' ' + doc).rjust(70, '=')
        rst = open(doc).read()
        original_tree = docutils.core.publish_parts(
                source=rst, 
                writer_name='pseudoxml')['whole']
        result = docutils.core.publish_parts(
                source=rst, 
                writer=init.LOSSLESS_WRITER.Writer())['whole']
        generated_tree = docutils.core.publish_parts(
                source=result,
                writer_name='pseudoxml')['whole']
        print "Doctree:", original_tree == generated_tree
        print "reST:", rst == result
        print "reST:", rst.strip() == result.strip()
        print
        print rst.strip()
        print
        print result.strip()

