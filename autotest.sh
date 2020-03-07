# DBのマイグレーションとpytestの実行を行う。(DockerfileのCMDで実行)
# データ収集はJob & CronJobで実施するので、Dockerファイルは分割する

# DBの疎通確認に成功するまで、DBマイグレーションとテスト実行を待つ
while :
do
  /bin/ping $POSTGRES_TEST_HOST -w1 -c1 &> /dev/null
  if [ $? = 0 ]; then
    echo "DB Connection OK. Autotest will start after 5 seconds."
    sleep 5
    break
  else
    sleep 5
  fi
done

python ./src/main/migrate.py
pytest -m 'smoke' --cov=./src/main ./src/test