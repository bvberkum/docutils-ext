_writers = dict(
    mpehtml='html',
    #mpelatex='latex2e',
    #mperst='rst',
    dotmpehtml='html',
    #dotmpelatex='latex2e',
    #xhtml='xhtml',
    #blhtml='xhtml',
    dotmperst='rst',
)

def get_writer_class(writer_name):
    """Return the Writer class from the `writer_name` module."""
    writer_name = writer_name.lower()
    #assert writer_name in _writers, writer_name
    if writer_name in _writers:
        writer_name = _writers[writer_name]
    module = __import__(writer_name, globals(), locals())
    return module.Writer


