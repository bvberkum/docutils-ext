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
  read_nix_style_file .upstream.tab | while read branch rest
  do
    for upstream in $rest
    do
      echo "Merging $branch from $upstream"
      git checkout -q $upstream || {
        echo "Error checking out $upstream"
        continue
      }
      git pull -q || {
        echo "Error updating $upstream"
        continue
      }
      git checkout -q $branch || {
        echo "Error checking out $branch "
        continue
      }
      git merge -q $upstream || {
        echo "Error merging $branch with $upstream"
        continue
      }
    done
  done
}


upgrade_all
git checkout master

