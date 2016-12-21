#!/bin/bash
# These correspond to python modules in dir ./test
# See test/main.py

case "$(whoami)" in
  travis|jenkins ) ;;
  # FIXME:du-ext.1: See about `test_1_get_reader_class` (comp) failure at Travis.
  * )
      echo comp
    ;;
esac

cat <<EOH

comp
builder
frontend
build
form
sql_storage
rstwriter

EOH


# TODO
#extractor
#mediawiki
#atlassianparser
#atlassianwriter
#confluence
#simplemuxdem

