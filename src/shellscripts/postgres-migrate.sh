bash ./src/shellscripts/postgres-healthcheck.sh
poetry run python ./src/main/migrate.py -i $INSERT_MASTER_DATA