Du suggestions
--------------
The good, the bad, the ugly. 


- Would be nice to have all errors in (XHTML) output accumulated into
  system-messages section, instead of embedded whereever they appear. 

  Looks better and makes more sense typographically-wise, a linked marker at 
  the origin location would suffice.

  universal.Messages, used in writer component, already does something related?
  perhaps I've been looking at to horrible publisher errors, need to reproduce.

- MD5 et. al. check-sum proposal.

- Breadcrumb paths proposal.

  A path in rooted tree, useful in hierarchical navigation.

  - custom nodes?
  - list vs. inline
  - plain vs. references

----

- ReStructuredText does not support **nested inline** syntax. In itself not
  entirely bad, but theres no support for nested/overlapping references and roles.
  Ie. no strong *and* reference, etc. 
  
  Somehow I find that totally brain-dead, but I realise
  that this might not be solved by plain text inline markup, so outside the
  scope of the rSt parser and may be even Du?

  Note that nested inline support is planned before Du becomes a Python stdlib
  package. See subversion branches.

- `strong`, `emphasis`, `title-reference` and `literal` have **alternative rSt
  inline syntax** and feel a lot more like the readable inline markup rSt is
  supposed to be. 
  
  (I don't like the role syntax, though I find it practical. 
  But the concept or inline Roles I think are very useful. My
  only concern with it is compatibility. Ie. authors may differ in their
  preferences for using inline markup, I just think the role directive does not
  go far enough.)
  
  What about per-document inliner settings. 
  If Du would allow these set,::
   
    then author A might write **strong** and *emphasis* in a document, 
    while author B writes *strong* and /emphasis/ in another.

    Both could read :strong:`strong` and :emphasis:`emphasis` if the inliner
    could be customized through document settings.

  The standard Du settings would be::

    --inline=``,literal
    --inline=`,title-reference
    --inline=*,emphasis
    --inline=**,strong

  There'd be a range of identifiers reserved for this, just like for headings.  
  (Reference syntax can be ignore because it is more complex?)

  And what about the typographical interesting cases of bracketed text, like
  ``()``\ -style inline comments, ``[]`` for abbreviation definitions or inline 
  comments, or additions by editor or in quotes. Hey, even using ``---`` (em-dash) 
  for branching thoughts in a 'regular' sentence.


- Inline text roles are defined in hierarchical fashion. 
  In std Du 8 inline document nodes are available to 'extend'. 
  What about 'multiple inheritance'?

----

- Document structure should be generic, not specific. 
  Martin Blais posted in 2005 a proposal to remove ``doctest`` and ``option_list``
  to the devel mailinglist. [#]_ 
  
  But some like it, others would ditch it if it could be subsumed by a more
  generic structure, and again others point out its not possible to go more
  generic without leaving specifics particular to options.

  I've been thinking of using profiles of Du, defined in Relax NG and use these
  to validate the XML DOM. 

.. [#] http://thread.gmane.org/gmane.text.docutils.devel/3316/focus=3354

- In 2007 Lea posted on the issues processing multi-part documents.
  No-one replied but the issues are interesting. [#]_


.. [#] http://thread.gmane.org/gmane.text.docutils.devel/4125

.. "$Id$"[3:-1]
