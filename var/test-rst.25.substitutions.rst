Substitution testing using the output comparison method is not completely
possible at the moment.

XXX: Maybe the rst2rst AST retains something about the original substitution
reference, but possibly this requires extending the reader and/or parser.

The following definition is easy. See -demo for things that are not.

.. |str| replace:: str data

With rst2rst, it seems safest to use ``node.rawsource`` to retrieve at least the argument string.

