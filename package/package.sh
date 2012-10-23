rm -rf dist
export DJHEROKU_MINOR_VERSION=`date +%Y%m%d%H%M%S`
virtualenv -q .venv
. .venv/bin/activate
pip install -r requirements-test.txt
./setup.py lint
nosetests
./setup.py sdist
