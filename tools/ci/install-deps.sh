set -e
pip install -r requirements.txt
pip install -r test-requirements.txt
pip install -r optional.txt || echo 'Optional Py lib install failed'
composer install
