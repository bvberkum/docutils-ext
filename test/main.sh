#!/bin/bash
# These correspond to python modules in dir ./test, passed as arguments to
# test/main.py. See Rules.mk's test_py_. rule.

#case "$(whoami)" in
#  travis|jenkins ) ;;
#  # FIXME:du-ext.1: See about `test_1_get_reader_class` (comp) failure at Travis.
#  * )
#      echo comp
#    ;;
#esac

cat <<EOH

builder
frontend
build
form
sql_storage
rstwriter
du_ext_transform_reference

EOH


# TODO
#extractor
#mediawiki
#atlassianparser
#atlassianwriter
#confluence
#simplemuxdem

