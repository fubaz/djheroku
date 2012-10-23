minor_version = os.environ.get('DJHEROKU_MINOR_VERSION', None)
rt DJHEROKU_MINOR_VERSION=`date +%Y%m%d%H%M%S`
virtualenv -q .venv
. .venv/bin/activate
pip install -r requirements-test.txt
./setup.py lint
nosetests
./setup.py sdist
