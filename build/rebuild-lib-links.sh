
test -n "$1" || set -- "/src"

ln -s /src/aafigure lib/aafigure
ln -s /src/python-docutils/docutils/docutils/docutils lib/docutils
ln -s /src/python-docutils/latest/branches lib/docutils-branches
ln -s /src/python-docutils/latest/branches/lossless-rst-writer/docutils lib/docutils-lossless
ln -s /src/python-docutils/latest/trunk/sandbox lib/docutils-sandbox
ln -s /src/nabu/working/lib/python/nabu lib/nabu

