set -e

test -x "$(which composer)" || {
  mkdir -vp ~/.local/{bin,lib,share}
  curl -sS https://getcomposer.org/installer | php -- --install-dir=$HOME/.local/bin --filename=composer
  ~/.local/bin/composer --version
}
