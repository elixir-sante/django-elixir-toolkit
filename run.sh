#!/bin/bash

echo "⚙️  Setting env variables"
export DJANGO_SECRET_KEY="X"

echo "☁️ Installing dev env (pipenv with --dev)"
pipenv install --dev
pipenv run python3 -m django --version

if test "$1" = "test"; then
    echo "🔥 Testing app"
	pipenv run coverage run --source='.' manage.py test -v 3
	pipenv run coverage report
	pipenv run coverage json
fi

if test "$1" = "migrate"; then
    echo "Migrating DB"
	pipenv run python3 manage.py makemigrations
	pipenv run python3 manage.py migrate
fi

if test "$1" = "serve"; then
	# pipenv run python3 manage.py collectstatic --clear --no-input
	pipenv run python3 manage.py runserver
fi
