
test -n "$1" || set -- "/src"

mkdir -vp lib
rm -rf lib/*

#ln -s $1/aafigure lib/aafigure
#ln -s $1/python-docutils/docutils/docutils/docutils lib/docutils
#ln -s $1/python-docutils/latest/branches lib/docutils-branches
ln -s $1/python-docutils/latest/branches/lossless-rst-writer/docutils lib/docutils-lossless
#ln -s $1/python-docutils/latest/trunk/sandbox lib/docutils-sandbox
ln -s $1/nabu/working/lib/python/nabu lib/nabu

