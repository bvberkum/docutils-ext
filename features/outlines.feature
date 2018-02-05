Feature: Outlines
  It should be possible to extract the values of nesting fields as outlines.

  Fields are defined by fieldset sepcification, prescribing a matcher and 
  parameters for a a field k

  matching elements based on type or other attributes.

  and providing validator

  DocumentVisitor
    - ``subClassOf:*`` resolve full classname, match any node implementing it.

    - ``node:<classname>`` - match if subclass of given node class name.

      E.g. ``node:Node`` for every node type, 
      ``node:Root`` or ``node:document`` for only the document node,
      ``node:definition_list``, etc. See also ``category``.

    - ``group:<name>`` match on named predefined group of multiple ``node:*`` types at once.

    - ``class:<classnames>``, ``attr:*``, ``<id>`` attribute matchers.

    Recursion
      Any schema that defines types on nodes containing block level elements
      becomes recursive, and can return a nested data structure.

    Configuration
      optparse::

        <id>[,<help>];[optparse:]<type>[,<require>[,<append>[,<editable>[,<disabled>]]]][;<vldtors>,]

      json-schema::
        
        <id>[,<help>];json:<type>[,<require>[,<append>[,<editable>[,<disabled>]]]][;<vldtors>,]



