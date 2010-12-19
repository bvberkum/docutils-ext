from inliner import Inliner


# No additional parser components,
# directives are registered with std rST parser.
_parsers = dict(
)

def get_parser_class(parser_name):
    """Return the Parser class from the `parser_name` module."""
    parser_name = parser_name.lower()
    if parser_name in _parsers:
        parser_name = _parsers[parser_name]
    module = __import__(parser_name, globals(), locals())
    return module.Parser
