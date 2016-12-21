#!/bin/bash
# These correspond to python modules in dir ./test
# See test/main.py

case "$(whoami)" in
  travis|jenkins ) ;; # FIXME: see about the recursion in build #72
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

rstwriter

EOH


# TODO
#extractor
#mediawiki
#atlassianparser
#atlassianwriter
#confluence
#simplemuxdem

