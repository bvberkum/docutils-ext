_writers = dict(
    mpehtml='html',
    mpelatex='latex2e',
    mperst='rst',
)

def get_writer_class(writer_name):
    """Return the Writer class from the `writer_name` module."""
    writer_name = writer_name.lower()
    if writer_name in _writers:
        writer_name = _writers[writer_name]
    module = __import__(writer_name, globals(), locals())
    return module.Writer


