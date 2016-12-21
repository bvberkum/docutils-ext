Branches
========

See ``.up.sh`` for automated downstream merging. Maybe rename file..

GIT
  master
    all development happened here until dev was branched.
    Sync with dev only.

  dev
    Sort of the master now. Testing only functional stuff, may be deceptive as
    not everything is unit/systemtested?

    :tests: 53; 18 failures, 35 OK

    dev_rstwriterobjects
      separate development branch for rstwriter restructuring,
      trying to OO-ify and add some elegance.

      :test: 57; 25 failures, 2 errors

    dev_simplemuxdem
      trying a lossless read/write using the rST SM base with a
      simple text format, to understand the rSt parser statemachine.

      :tests: 53; 18 failures, 35 OK

      Abandoned while I do get more insight into the rSt parser
      machinery.

    dev_rstwriter
      While things left to be desired before finishing dev_rstwriterobjects,
      implement and test reStructuredText writer.

      :tests: 66, 9 failed

    `f-rst-forms`_
      Splitting topic of dev for separate testing. Possibly a few hacks while
      core/frontend is in flux.

    dev-outlines
      Extract outlines from rST. See `Feature: Outlines`__

    subtree (current 2012-04-14)
      experimenting with git-subtree, adding rst2confluence writer

      :tests: 53; 22 failures, 1 error, 30 OK

.. __: features/outlines.features

.. include:: .refs.BranchDocs.rst


