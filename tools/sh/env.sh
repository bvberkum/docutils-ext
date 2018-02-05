
# Easiest way I see to add dev checkout to env
export PYTHONPATH=.:$PYTHONPATH:test


# Load virtualenv (should be initialized by htd run init)
test -d ~/.pyvenv/du-ext && {
    htd ispyvenv || {
        source ~/.pyvenv/du-ext/bin/activate;
    }
}

