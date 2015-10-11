test -e $HOME/src/python-docutils/docutils-svn || {

    # checkout subpath to keep time/size down

    mkdir -vp $HOME/src/python-docutils/docutils-svn/branches
    svn checkout -q http://svn.code.sf.net/p/docutils/code/branches/lossless-rst-writer \
        $HOME/src/python-docutils/docutils-svn/branches/lossless-rst-writer

    ln -s docutils-svn $HOME/src/python-docutils/latest
}
