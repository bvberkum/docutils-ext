TEST
=========

Basic inline constructs
-----------------------

`Title reference`

``Inline literal``

`Anonymous reference`__

.. __: anonymous-target

.. role:: myclass

`myclass` is a custom inline role: :myclass:`Some special text.`

Section
-------
term
    definition

----

`Anonymous HREF <//href/path>`__
`Inline reference`_ source.
_`Inline reference` target.

See `a named relative link`_ for details.

.. _A Named Relative Link: name#1

----

`title reference`

``literal``

```test```

/test/

*emphasis*

**strong**

Inline ideas
=============
Normal role usage::

  .. role:: a
     :class: agent
  
  - :a:`Opera`
  - `Mozilla`:a:
  
.. default-role:: title-reference


Roles can extend an standard inline, there's 10 of them:

- Emphasis
- String
- Literal 
- Title, PEP or RFC Reference  
- Super and Subscript
- Abbreviation
- Acronym  

Reference elements are not usable as role, see section below.

The cool thing is that the PEP or RFC roles are parsed. Would I write `2822` in
the RFC role then upon parsing it is replaced by reference: :rfc-reference:`2822`.

Note that role definitions are an rSt feature not parsed into
the document structure.


On roles and references
------------------------
A quote refers to external text, possibly included in edited form. Also there
are use cases where editor comments may be part of a published text. A Title
Reference text may refer to an external title, but retrieving it is left to the
user.

Generally speaking, making an 'hypertext' reference is something an author must 
explicitly do. This is how Du/rSt implements this. 
And there is another part to writing such a reference: defining its **target**.

In normal 'standalone' rSt, each target is explicitly written out. 
And because targets are part of the document, the publisher only needs to look
them up by name; no further need to manage addressable content.
The publisher does make a provision though to look up unknown references,
bringing into perspective a non-standalone publisher with addressable content
storage. (However, leaving location of that target definition somewhat undefined, 
or bound to implementation.)


To get back to roles and references; both are explicit constructs deployed by
the author.

A document not only defines what text is presented to a reader, but also its 
structure; writers author text *and* structure.

But, references are also a front-end feature.



More roles
------------
I could do with some more roles, or customized notation. E.g. to let Nabu
extract data in a non-fuzzy way there need to be some elements to watch for.
Also within a certain application, such as source-code documentation, there are
`easily tens of different roles`__, or `namespaces` to consider making inline references too.

.. __: http://sphinx.pocoo.org/markup/inline.html#cross-referencing-syntax

My idea is:

- to cut a down on the verbosity of writing in an inline role at the cost of
  being explicit.
- by default only parse standard role notation, ie. publisher requires options
  or flags set. (Currently, any roles or the default-role are rSt markup features
  only, processed and stripped by the rSt parser.)

My proposals:

1. make the default-role configurable by command-line.
2. Customizable inline-delineators attached to each role, by rSt markup and
   command-line options.


-  :`foo command`
-  /`Foo path name`
-  -`Foo option`
-  --`Foo option`


These all need escaping:

-  Perhaps some PHP or JS identifier $\ `Foo command`
-  Or HTTP home-dirs ~\ `myuser-id`
-  A MS option or path perhaps \\ `Foo path name`
-  +\ `Foo option`
-  ^\ `Foo pattern` 
-  @\ `Foo host` 
-  &\ `Foo param` 
-  #\ `Foo fragment` 
-  §\ `Foo command`
-  §\ `Foo command`

Honestly, escaping doesn't look all that bad on readability.
But no escaping is preferred.

-  Considering :\ `Foo Bar` vs. :`Foo Bar`

Quoting text also serves to discern it from regular body text.

- There's regular quotes, "`Foo option`".
- Informal comments by the author (`comment`).
- Or the additions made by an editor. [`comment, Ed.`]
- And other crazy constructs in some local documentation effort; <`Foo tag`>,
  {`Foo var`}. 

These I find far more readable.


