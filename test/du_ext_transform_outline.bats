#!/usr/bin/env bats

load helper
bin=./tools/build.py


setup()
{
  . ./tools/sh/env.sh
  TESTFILES="var/test-common.1.definition-tree.rst "\
"var/test-rst.9.definition-list-1.rst "\
"var/test-rst.9.definition-list-2.rst"
}

@test "build.py can record outline" {

  for tf in $TESTFILES
  do
    python tools/rst2pprint \
      --traceback \
                --record-outline=/tmp/outline.list \
                --record-outline-format=path \
                $tf /dev/null
  done
  #test $(filesize /tmp/outline.list) -eq 208

  #test "$(cat /tmp/outline.list)" = "$(cat <<EOM
#EOM
#  )"
}
