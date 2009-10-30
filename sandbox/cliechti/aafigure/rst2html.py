#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision: 5654 $
# Date: $Date: 2008-09-30 17:05:46 +0200 (Die, 30 Sep 2008) $
# Copyright: This module has been placed in the public domain.

"""
A minimal front end to the Docutils Publisher, producing HTML.
"""

import locale
try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, Publisher, default_description

import aafigure_directive
aafigure_directive.register()  # Enable the ABC directive

description = ('Generates (X)HTML documents from standalone reStructuredText '
               'sources.  ' + default_description)

publish_cmdline(writer_name='html', description=description)
