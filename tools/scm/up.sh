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
        return 1
      }
      git pull -q || {
        echo "Error updating $upstream"
        return 1
      }
      git checkout -q $branch || {
        echo "Error checking out $branch "
        return 1
      }
      git rebase -q $upstream || {
        echo "Error rebasing $branch with $upstream"
        return 1
      }
      echo "Downstream $branch up-to-date with $upstream"
    done
  done
}


upgrade_all
git checkout master

