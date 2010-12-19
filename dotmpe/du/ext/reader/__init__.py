_readers = dict(
    mpe='mpe',
    dotmpe='mpe',
    mkdoc='mkdoc',
)

def get_reader_class(reader_name):
    """Return the Reader class from the `reader_name` module."""
    reader_name = reader_name.lower()
    if reader_name in _readers:
        reader_name = _readers[reader_name]
    module = __import__(reader_name, globals(), locals())
    return module.Reader

