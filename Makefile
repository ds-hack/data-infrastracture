up-local:
	kubectl apply -f ./kubernetes/local/deploy

down-local:
	kubectl delete -f ./kubernetes/local/deploy

# PostgreSQLは日時でカスタム形式のバックアップをとる(初回はdbdump/postgresディレクトリを作成後実行)
# DBの接続情報は環境変数経由で指定
pg_logical_backup:
	pg_dump "-Fc" -h "${DSHACK_PG_HOST}" -p "${DSHACK_PG_PORT}" -U "${DSHACK_PG_USER}" -d "${DSHACK_PG_DBNAME}" > dbdump/postgres/dshack_devdb_$(shell date +"%Y%m%d").custom

# ダンプファイルのPathは、コマンドライン引数として与える(ex. make pg_all_restore DUMP_FILE_PATH="...")
pg_logical_restore:
	pg_restore -h ${DSHACK_PG_HOST} -p ${DSHACK_PG_PORT} -U ${DSHACK_PG_USER} -d ${DSHACK_PG_DBNAME} < ${DUMP_FILE_PATH}