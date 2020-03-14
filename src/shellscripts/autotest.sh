bash ./src/shellscripts/postgres-healthcheck.sh
poetry run pytest -m 'smoke' --cov=./src/main ./src/test