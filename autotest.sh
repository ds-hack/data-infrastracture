# DBのマイグレーションとpytestの実行を行う。(DockerfileのCMDで実行)
# データ収集はJob & CronJobで実施するので、Dockerファイルは分割する
sleep 5
python ./src/main/migrate.py
pytest --cov=./src/main ./src/test