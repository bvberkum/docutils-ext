
mkdir -vp $HOME/src/nabu
test -d $HOME/src/nabu/nabu-hg || {
    hg clone https://bitbucket.org/blais/nabu $HOME/src/nabu/nabu-hg
    ln -s nabu-hg $HOME/src/nabu/working
}
