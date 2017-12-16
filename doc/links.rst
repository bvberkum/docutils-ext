:created: 2011-01-12
:updated: 2013-11-19
:description:
  reStructuredText has a construct to write meta elements from flat lists.
  But there is not a way to explicitly write out complete links, or to specify
  the relation that is made by a reference.

  HTML does have a construct for this, and I think such a feature is an
  important one in writing hypertext.

.. contents::

Links are always made up of two different endpoints described at different locations,
except in the case of anonymous links, which are single inline constructs but
which still will have a target point. I think about it as a blank node in a
network graph but I should check rST references/targets out further.

In HTML it is possible to provide for link descriptions in the document header
(but which often are not granted any real estate by the browser though).
Nevertheless, these are *essential* for writing Web pages.

So whatever the feelings about HTML or the use for such a structure in output formats other than HTML, I personally believe it is a usefull and on the Web perhaps even underused feature.
At the very least, without it the following is impossible:

- specifying the style document to be used with the current document.
- specifying the current document as a node in a sequence or graph.
  E.g. to link to the owner or to provide previous/next metadata.

Though the latter is to some extent possible through anchors and other elements, iow. falling back to (X)HTML in concord with microformats.

I believe a link element is needed, but perhaps more so as a sort of plumbing for new transforms or markup directives.

Links in HTML
--------------
At its simplest form, the functionality offered by HTML is expressed in::

  .. link:: http://dotmpe.com/media/style/default.css
     :rel: stylesheet

  .. link:: Default stylesheet
     :href: http://dotmpe.com/media/style/default.css
     :type: text/css
     :rel: stylesheet

The relation (``rel`` attribute) is available for anchors (``<a/>``) in HTML too.
Some values are listed in rel-values.

But in HTML, ``link`` definitions are made in the document's header, and not in any way tied to the anchors within the document.
Perhaps there is some microformat that extends on that, I don't know.

HTML links are directed.
Without the ``rev`` attribute the links are at the origin point of the relation,
but can or should sometimes be stored at the destination point.
Lets introduce storage point and reference point to indicate link endpoints
based on storage regardless of their direction.

Because HTML introduces a peculiarity.
The reference-poin may be some kind of HTML anchor, because the URI-ref may include a fragment identifier.
Addressing document substructures using URI-ref 'hash' or 'fragment' identifiers
is not really a well-defined practice.
For XML in general W3C has settled on matching element ID attributes with this
URI part and so containers in the document can be addressable.

Again a microformat may step in.
The goal would be to have multiple origin points and target points in two
distinct sets ``from`` and ``to``, and a third one of such a set to denote type.
Perhaps a fourth ``homedoc`` to indicate the storage location.
That would be the full Xanadu 88.1 spec I think for links and their end-sets.

Being pragmatically and looking at the web and past semweb efforts, a single
span endset may just suffice.

In any case a new URI format for such a beast would be needed?


reST
------
In docutils, links are usually made of an inline reference, and a target description.
The latter of which is an invisible element.

The target may be expressed by an URL, or the id for a local, named anchor.
Named anchors may also be written inline or as named target.
But other constructs than anchors may be candidates for named targets too.

To define an additional directive that can further describe these references as
typed links between document (parts), these names are essential.
The alternative would be using document object model paths, an solid but clunky
and in reST an arguable un-elegant solution.

Link types we can readily discern in standard docutils are:

- footnote (and backref) needs little explanation, these go to the end of the page,
  section or document.
- citation (and backref) is a variation on footnote where the reference is not a
  sign or number but a symbol of several characters usually, regulary used in
  papers.
- content table (and backref) go from the overview to the section header.
- also some forms of errors are collected into an appendix and linked to
  identify the erroneous markup.


A broad brush
---------------

Taking HTML as example, the complete list of options could be:

::

  .. link:: url-or-name
     :name: used to generate id
     :id: explicit-id
     :href:
     :hreflang:
     :rel:
     :rev:
     :type:
     :media:

Where the type describes the content type of the target resource,
not the type of the link itself, which is expressed by the relation.
This relation is indicated by a forward or backward label.

This in basis is good to express relations between documents.
But afaics there are two issues still:

1. There is really only a standard for single-point targets.
2. There is no standard interaction between anchors and links.

Also, reStructuredText already facilitates in defining targets using URLs.
Lets reuse this.

----

The following gives the two endpoints of the simplest form of reference in
Du/reST::

  .. _name:

  The link `name`_ refers to this paragraph.

and to immedeatly extend this example a little::

  .. _name:

  This link `name`_ refers to this paragraph.
  And `name`_ referred to it again and again__, etc_, possibly from other documents.

  .. __: `name`_
  .. _etc: `name`_

  We could also have written it inline, like to _`a target name` from `a target name`_.

Note the repetition of multiple references for the same target,
and the reusing of the the reference in a new anonymous and new named target definition.

(Instead of names, an URL could be used).

Now, this renders to:

.. topic:: Example

  .. _name:

  This link `name`_ refers to this paragraph.
  And `name`_ referred to it again and again__, etc_, possibly from other documents.

  .. __: `name`_
  .. _etc: `name`_

  We could also have written it inline, like to _`a target name` from `a target name`_.


The fragment according to this text is::

  <target refid="name">
  <paragraph ids="name" names="name">
      This link
      <reference name="name" refid="name">
          name
       refers to this paragraph.


Note that the target and the reference share the same name.
Here is the rest::

  ...
      And
      <reference name="name" refid="name">
          name
       referred to it again and
      <reference anonymous="1" name="again" refid="name">
          again
      ,
      <reference name="etc" refid="name">
          etc
      , possibly from other documents.
  <target anonymous="1" ids="id1" refid="name">
  <target ids="etc" names="etc" refid="name">
  <paragraph>
      We could also have written it inline, like to
      <target ids="a-target-name" names="a\ target\ name">
          a target name
       from
      <reference name="a target name" refid="a-target-name">
          a target name
      .

----

The link directive can use a title or name to claim a new link or 'tie' a relation to an existing reference by name

If we add this to the previous example::

  .. link:: Link name
     :rel: jump

Then the first part of the structure could look like::

   <target refid="link-name">
   <paragraph ids="link-name" names="link\ name">
       Link target is this paragraph, where
       <reference name="link name" refid="link-name" relation="jump">
           link name
        refers too.

There does not seem to be an immediate need for an additional document node, and
the target could be pruned now.
The original reference node can bear the relation indicator, but this does raise the question what the new directive will match on.

Matching on name narrows the scope of the link to a set of literally equal references,
whereas matching on ``refid`` results in a broader set of *all* references to a target.
This includes the whole chain of targets that (eventually) resolve to this ``refid``,
with named and anonymous targets.
(Anonymous targets could be matched on their index, but note that Du allows for
``--strip-anonymous-targets``).

----

Perhaps the extra directive is unnecessary, if the reST target definition itself accepts options.
This may not be the case or not in any way extensible currently.
Perhaps it would be a more elegant way to parametrize the reference/target relation,
as separate ``link`` directives may get lost or break and in net. result ask of extra effort from the author.

----

One thing left before listing the final set of options: stand-alone links.
Ie. those not tied to any literal inline reference but making hidden references (though an interpreting client *should* list or *may* handle it).

A good but boring example is a CSS stylesheet, so lets try another relation::

  .. link:: Page 2
     :rel: next
  .. _page-2: ./page-2.rst

which by more extensive hacking might be an elaboration on standard reST syntax::

  .. _page-2: ./page-2.rst
     :rel: next
     :title: Page 2

(The `title` may be given if the link does not appear in the text, whereas the
`link` directive would require it without further matching options).

For more examples of relations between HTML documents see the `W3C REC on HTML401`__.

.. __: http://www.w3.org/TR/html401/struct/links.html#h-12.3

----

Directive ``link``:

.. parsed-literal::

  **..link::** `[link title]`
     [opts]

Options
  ``name``
     Normally set to whatever is given as argument, should be used as label by interpreting clients.
  ``refname``
     Optional, match on references with given `name`.
  ``refid``
     Optional, match on target refid with given value instead.
  blankid?
     Optional, match for anonymous target on index instead.
  ``rel``
     The indicator for the reference-target relation type.
  ``rev``
     The indicator for the target-reference relation type.
  ``inv``
     Inverse the relation.

If a `name`  is provided as argument, it serves as `name` *and* ``refname``.
Otherwise `name` should be specified and no argument given to the directive.
Matching may be overridden by ``refid``,
possibly blankid (and then what about the other indices: messages, errors,
footnotes, sections).

----

Left undiscussed here:

- The types of relation, wether it is symmetric and what labels are used to indicate an endpoint.
  and how the direction of the link and thus of the rel/rev semantics might be changed by an additional flag.

.. include:: .defaults.rst
