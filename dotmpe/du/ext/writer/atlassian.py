from docutils import writers


class Writer(writers.Writer):

    def __init__(self):
        writers.Writer.__init__(self)


