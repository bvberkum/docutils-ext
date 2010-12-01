from docutils import utils
from docutils.parsers.rst import roles

from dotmpe.du.ext.node import figureref


def fig_role(role, rawtext, text, lineno, inliner, options={}, content=[]):
    text = utils.unescape(text)
    node = figureref.figure_ref('(?)', '(?)', target=text)
    return [node], []

roles.register_canonical_role('fig', fig_role)


