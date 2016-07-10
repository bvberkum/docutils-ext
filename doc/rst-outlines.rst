
Many composite forms of outlines are possible working with literal data.
The objective is to extract outline definitions, a generic structure
of only a handfull of types.

- Folder
- Item
- Separator

* Outline (root)

See feature for terse specs.
test/var/outline-1 for config sketches.


Reference
---------
Inventory (partial) of Du nodes package
  functional node base classes
    - Node
    - Text(Node)
    - Element(Node)
    - TextElement(Element)
    - FixedTextElement(TextElement)

  Mixins
    - Resolve
    - BackLinkable

  Element Categories
    - Root
    - Titular

    ...

    - Targetable(Resolvable)
    - Labeled

  Elements
    - document(Root, Structural, Element)

    Title Elements
      - title(Titular, PreBibliographic, TextElement)
      - subtitle(Titular, PreBibliographic, TextElement)
      - rubric(Titular, TextElement)

    Bibliographic Elements
      ..
    Decorative Elements
      ..
    Structural Elements
      - section(Structural, Element)
      - topic(Structural, Element)
      - sidebar(Structural, Element)
      - transition(Structural, Element)

    Body Elements
      - paragraph(General, TextElement)
      - compound(General, TextElement)

      ...

      - system_message(Special, BackLinkable, PreBibliographic, Element)
      - pending(Special, Invisible, Element)
      - raw(Special, Inline, PreBibliographic, FixedTextElement)

    Inline Elements
      ...

      - image(General, Inline, Element)
      - inline(Inline, TextElement)
      - problematic(Inline, TextElement)
      - generated(Inline, TextElement)

    Auxiliary Classes, Functions, and Data
      ..


