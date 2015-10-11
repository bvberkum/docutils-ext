
test -d $HOME/src/nabu/nabu-hg || {
    mkdir -vp $HOME/src/nabu
    hg clone https://bitbucket.org/blais/nabu $HOME/src/nabu/nabu-hg
    ln -s nabu-hg $HOME/src/nabu/working
}
