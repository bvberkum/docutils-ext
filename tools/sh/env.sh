
set -e

# Easiest way I see to add dev checkout to env
export PYTHONPATH=.:$PYTHONPATH:test

export PATH=tools:$PATH


# Load virtualenv (should be initialized by htd run init)
test ! -d ~/.pyvenv/du-ext || {

  test ! -x "$(which htd)" || {
    htd ispyvenv || {
        source ~/.pyvenv/du-ext/bin/activate;
    }
  }
}
