#!/bin/bash
# These correspond to python modules in dir ./test
# See test/main.py

case "$(whoami)" in
  travis|jenkins ) ;;
  * )
      echo comp
    ;;
esac

cat <<EOH

builder
frontend
build
form
sql_storage

# FIXME
rstwriter

# TODO
#extractor
#mediawiki
#atlassianparser
#atlassianwriter
#confluence
#simplemuxdem

EOH


