#!/usr/bin/env bats

load helper
bin=./tools/build.py

setup()
{
  . ./tools/sh/env.sh
}

@test "${bin} --help" {

  run ${bin} --help
  test_ok_nonempty
}

@test "${bin} no-such-file" {

  run ${bin} no-such-file
  test_nok_nonempty
}
