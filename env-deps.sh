
case "$ENV_NAME" in
  dev)
      echo build-essential
      echo hg
      echo git
    ;;
esac

case "$1" in
  apt )
      echo graphviz
      echo plotutils
      echo python-docutils
    ;;
esac

