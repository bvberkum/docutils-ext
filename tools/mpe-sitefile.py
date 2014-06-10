#!/usr/bin/env python
"""
Sitefile idea
    store: 'Sitefile' | 'sitefile:///./build/sitefile.sqlite'
    main: 
        title:
        roles:
        docinfo:
        <section-id>:
            title:
        includes: 
            - foo/main
        footnotes:
        references:
    foo/main:
        title:
        includes:
            - foo/bar/main
    foo/bar/main:
        title:

1. Build/update sitefile from source files::

    mpe-sitefile update <sitefile>.yaml *.rst

2. Build target document(s) from sitefile

    mpe-sitefile gen-grunt  

    mpe-sitefile gen-make
    
    %.html: %.rst
        rst-site2html <sitefile> $< $@

Effectively builts a database.
Something readable for any processing program.
Sitefile is a collection of file-extracted objects.

May want to imagine using an object database instead to store fileobjects.
Rewriting the sitefile may not be really appropiate.
Instead, Sitefile can list external metadata. 

Generated data, may be merged, can go into include (ie file store) or into object store.

"""
import os
import sys
import yaml


sitedef = 'Sitefile'
siteenv = 'SITE'
siterc = '.siterc'

def main():
	env = os.getenv('SITE')
	if not env:
		if os.path.exists(siterc):
			env = open(siterc).read().strip()
		else:
			env = sitedef
	if not os.path.exists(env):
		env = env + '.yaml'
	assert os.path.exists(env), env

	sitefile = yaml.load(open(env))
	print yaml.dump(sitefile)

if __name__ == '__main__':
	main()

