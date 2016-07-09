#!/bin/sh

set -e

read_nix_style_file()
{
  cat $@ | grep -Ev '^\s*(#.*|\s*)$'
}

upgrade_current()
{
  local branch=
  grep '^'$branch .upstream.tab | while read branch rest
  do
    git merge $upstream
  done
}

upgrade_all()
{
  read_nix_style_file .upstream.tab | while read branch res
  do
    for upstream in $rest
    do
      git checkout $upstream || return $?
      git pull origin $upstream || return $?
      echo git checkout $branch
      echo git merge $upstream
    done
  done
}


upgrade_all

