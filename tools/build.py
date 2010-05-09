#!/usr/bin/env python
"""
Simple CLI front-end for dotmpe.du.builder.
"""

import sys, os
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__),
    '..', 'lib')))
from dotmpe.du.comp import get_builder_class
from dotmpe.du.util import read_buildline

#import logging
#logging.basicConfig()
#logger = logging.getLogger(__name__)
#logger.info(__name__)

writer = None

args = sys.argv[:]
source_id = args.pop()
while args:
    arg = args.pop()
    if arg.lower() in ('html', 'xml', 'pseudoxml'):
        writer=arg

source = open(source_id).read()

buildline = read_buildline(source, default_module='bluelines',
        default_class='AliasFormPage')
builder = None
#print writer, buildline
builder = get_builder_class(*buildline)()
try:
    builder = get_builder_class(*buildline)()
except ImportError, e:
    print >> sys.stderr, "No such builder %s" % buildline[0]
    sys.exit()
except AttributeError, e:
    print >> sys.stderr, "No such builder class '%s'." % buildline[1]
    sys.exit()

builder.initialize()
document = builder.build(source, source_id)

builder.render(document, writer_name=writer)

builder.prepare()
#builder.process(document)
#form_store = builder.extractors[0][1]

#from pprint import pformat
#print pformat(form_store.form_settings)

