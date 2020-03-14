# DBの疎通確認を行う
# TODO: kubernetesの機能でDB接続が可能かの確認を行ってから、Jobを実行することができる場合、その方法に切り替える。
while :
do
  /bin/ping $POSTGRES_HOST -w1 -c1 &> /dev/null
  if [ $? = 0 ]; then
    echo "DB Connection OK. Autotest will start after 10 seconds."
    sleep 10
    break
  else
    sleep 1
  fi
done