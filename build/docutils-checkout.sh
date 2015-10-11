test -e $HOME/src/python-docutils/docutils-svn || {
    mkdir -vp $HOME/src/python-docutils
    svn checkout http://svn.berlios.de/svnroot/repos/docutils $HOME/src/python-docutils/docutils-svn
    ln -s docutils-svn $HOME/src/python-docutils/working
}
