#!/usr/bin/env python
"""
:created: 2014-06-10

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


class Storage:

  @classmethod
  def parseRef(klass, storeref):
    p = storeref.find(':')
    scheme, opaque = storeref[:p], storeref[p+1:]
    storageClass = globals()[scheme.title()+'Storage']
    storageParams = storageClass.parseRefArgs(opaque)
    return storageClass, storageParams

  @classmethod
  def parseRefArgs(klass, value):
    return [value]

  @staticmethod
  def init(sitefile, proc):
    setting = sitefile['options']['store']
    if not isinstance(setting, list):
      setting = [setting]
    for storeref in setting:
      storageClass, storageParams = Storage.parseRef(storeref)
      if storageClass == SitefileStorage and storageParams[0] == '':
        storageParams = [proc['sitefile']]
      store = storageClass(*storageParams)
      yield store


class SitefileStorage(Storage):

  def __init__(self, sitefile):
    self.sitefile = sitefile

  def __str__(self):
    return "<%s:%s>" % ( self.__class__.__name__, self.sitefile )


class SitedirStorage(Storage):

  def __init__(self, sitedir):
    self.sitedir = sitedir

  def __str__(self):
    return "<%s:%s>" % ( self.__class__.__name__, self.sitedir )

  @classmethod
  def parseRefArgs(klass, value):
    assert os.path.exists(value) and os.path.isdir(value), value
    return [value]


class SitestoreStorage(Storage):

  def __init__(self, connection):
    self.connection = connection

  def __str__(self):
    return "<%s:%s>" % ( self.__class__.__name__, self.connection )

  @classmethod
  def parseRefArgs(klass, value):
    import sqlite3
    return [sqlite3.connect(value)]


class StorageManager:

  """
  Facade for set of stores.
  """

  def __init__(self, sitefile, proc):
    self.stores = list(Storage.init(sitefile, proc))

  def commit(self):
    pass


# Command handlers

def status(sitefile, proc):
  stores = list(Storage.init(sitefile, proc))
  print 'TODO status', stores, proc
  # TODO: perhaps print some storage stats

def update(sitefile, proc):
  stores = list(Storage.init(sitefile, proc))
  print 'TODO update', stores, proc
  # TODO: take on arguments and process, store results


# main entrypoint

def main(argv):
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
  if argv:
    cmdid = argv.pop(0)
  else:
    cmdid = 'status'
  proc = dict( sitefile=env, argv=argv )
  globals()[cmdid](sitefile, proc)

if __name__ == '__main__':
  argv = sys.argv
  scriptname = argv.pop(0)
  main(argv)
