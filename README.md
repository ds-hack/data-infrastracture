# Data-infrastructure

データ基盤(DW)構築用リポジトリ

当リポジトリ以外に、

- データハンドリング・MLモデル学習バッチを行うリポジトリ
- 各種サービスAPIを扱うリポジトリ
- Webアプリケーション・ダッシュボード等のプロダクトを扱うリポジトリ

を1つ以上作成する予定。

## システム構想

分析システムを作るモチベーションは、様々な種類のデータ収集・データハンドリング・分析・可視化・モデリング・アプリケーション構築等の一連の工程を、拡張・再利用可能な形で残すことを主としている。

### マイクロサービスアーキテクチャ

分析システムは探索的であり、変化に強いシステムが必要。システムの一部を切り捨てて、新しくすることも考えられるので、個々のシステムは疎結合にしたい。

### Immutable Infrastructure

システムが本格化すると、動作環境をローカルからクラウドに移す可能性が高い。Immutableなコンテナ上での開発によりローカルからクラウドへの移行時、また開発メンバーの追加時に環境起因の障害を最小限にしたい。

### CI/CD

システム要件の追加・変更時のコストを可能な限り減らす形で、CI/CDを導入する。

![system architecture](https://user-images.githubusercontent.com/56133802/75120700-c6fee000-56d0-11ea-9aef-3acb68ee168e.png)

## インストール

開発環境の構築には、下記のインストールが必要。インストール方法はOSにより異なるため詳しくは公式を参照のこと。

### Docker

Docker CEのインストール。Docker hubのアカウントを作成し、手順に従ってダウンロード&インストール。

- [Docker for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
- [Docker for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac)

### kubectlコマンド

kubectlコマンドは、k8sクラスタを操作するためのCLI。公式に沿ってインストール。

[kubernetes公式(kubectl)](https://kubernetes.io/ja/docs/tasks/tools/install-kubectl/)

（参考）mac OS

```bash
brew install kubernetes-cli
```

### minikube

ローカルで動作させるシングルノードのKubernetes。公式に沿ってインストール。

[kubernetes公式(minikube)](https://kubernetes.io/docs/tasks/tools/install-minikube/)

（参考）mac OS

```bash
brew cask install minikube
# brew updade minikube  # update時
minikube start  # 仮想マシン起動
```

### skaffold

Skaffoldはkubernetesを使ったアプリケーション開発において継続的デプロイをサポートするOSS。リポジトリ直下のskaffold.yamlに設定を記載する。

[skaffold公式ドキュメント](https://skaffold.dev/docs/install/)

```bash
brew install skaffold
```

## ローカルデプロイ

事前に`minikube start`により、minikubeを起動しておく。

Skaffoldによりローカルでユニットテストとデプロイの自動化を行う。コマンドはシンプル。

```bash
skaffold dev
```

Skaffoldはskaffold.yamlを読み取り、下記のタスクを担ってくれる。

1. Dockerfileによるイメージファイルのビルド
2. ビルドイメージのtag付け
3. 上記イメージを利用するk8s manifestファイルの更新
4. kubectl apply -fコマンドによるk8s manifestのデプロイ
5. podログのストリーミング

一度`skaffold dev`を叩いたあとは、ソースコードの保存を契機に1.〜5.が自動的に回る。

- 参考: Skaffold Pipelines

![workflow](https://user-images.githubusercontent.com/56133802/75913216-e1397a80-5e95-11ea-8e94-479eab9f645b.png)

自動テスト完了後、通常のローカルデプロイを実施したい場合は、makeコマンドをインストールした状態で、

```bash
make up-local  # 起動
```

```bash
make down-local  # 停止
```

により、ローカルデプロイに必要なコンテナ群の起動と停止をまとめて行うことができる。

## クラウドデプロイ

コストとの相談で随時クラウドに移行していく予定。当面はローカルデプロイのみ。

## k8sアーキテクチャ

クラウド展開時に改めて検討。

## データベース

ベースイメージは公式の`postgres:12.1`。DB処理はSQLAlchemyのORM機能を使用している。

データベースの接続情報などの秘匿情報は、dshack-secret.yamlで管理し、内容はリポジトリ管理対象外とする。

テンプレートは`tmpl/dshack-secret.yaml.tmpl`をもとに各自のローカルリポジトリで作成・管理する。

```yaml
apiVersion: v1
kind: Secret
metadata:
  namespace: dshack-development
  name: postgres-secret
type: Opaque
data:
  dbname: <<DB Name>>
  testdbname: <<TestDB Name>>
  username: <<DB Username>>
  password: <<DB Password>>
```

Kubernetes Secretには、そのままの文字列ではなくbase64エンコーディングで加工後の文字列を格納する。

例として`dshack`をDB名としたい場合、

```bash
% echo -n "dshack" | base64 -
ZHNoYWNr
```

より、`ZHNoYWNr`の値をyamlに記載する。

ローカル開発環境では手元のSQLクライアントからDBに接続できると便利なので、k8sクラスタ内でのみ利用できるHeadless Serviceと、外部から接続可能なNodePort Serviceを利用している。

SQLクライアントからは、下記の認証情報を使ってコンテナ上のDBに接続できる。

- ホスト名: `minikube ip`コマンドで表示されるIPアドレスを指定
- ポート: 開発用DBは30010、テスト用DBは30011を指定
- DB名: dshack-secret.yamlの設定値を指定
- ユーザー名: dshack-secret.yamlの設定値を指定
- パスワード: dshack-secret.yamlの設定値を指定

クラスタ内部からは、Headless Service + Stateful Setの組み合わせでPod名による名前解決を利用し、`<Pod名>.<Service名>.<NameSpace>.svc.cluster.local`によりIPアドレスを得ることができる。

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  namespace: dshack-development
  name: dshack-config
data:
  # StatefulSetの名前解決 (Pod名.Service名.Namespace名.svc.cluster.local)
  POSTGRES_HOST: postgres-sts-0.postgres-svc.dshack-development.svc.cluster.local
  POSTGRES_TEST_HOST: postgres-test-sts-0.postgres-test-svc.dshack-development.svc.cluster.local
  POSTGRES_PORT: "5432"
  POSTGRES_TEST_PORT: "5432"
```

上記はdshack-development.yamlの先頭にkubernetes ConfigMapとして設定しており、コンテナ内部からのDB接続情報(ホスト名+ポート)としては、こちらを使用する。

### データモデル

DBのドキュメンテーションに役立つ[SchemaSpy](http://schemaspy.org/)を活用している。

[Github Pages(プロジェクトサイト)](https://ds-hack.github.io/data-infrastracture/index.html)で公開しています。

1. `./datamodel/schemaspy.sh.tmpl`にDBの接続情報を入力し、`schemaspy.sh`としてローカル保存する。
2. 次のコマンドにより、`./schema`フォルダ以下にテーブル情報・フィールド情報・ER図などが出力される。
```bash
cd datamodel
bash ./schemaspy.sh
```
3. `./schema`フォルダ以下の`index.html`をブラウザで開くとダッシュボードが表示される。

<img width="1428" alt="schemaspy" src="https://user-images.githubusercontent.com/56133802/76035174-289e3480-5f84-11ea-95f9-553021b715a2.png">

<img width="563" alt="schemaspy-er" src="https://user-images.githubusercontent.com/56133802/76035232-54211f00-5f84-11ea-9fbd-ca1b5d9ca62a.png">

ER図は外部参照制約を基に付けているため、適切に制約が付けられているかが視覚的に分かる。テーブルやフィールドのコメントもダッシュボードに反映される。

### バックアップとリストア

`pg_dump`によるバックアップコマンドをMakefileに用意している。

PostgreSQLのバックアップ形式には大きく分けて、プレーンテキスト形式・カスタム形式・tar形式があるが、容量が小さいカスタム形式を採用している。

データベースの接続情報は各自の`.bashprofile`等に環境変数の設定を追加するなどしておく。

```Makefile
# PostgreSQLは日時でカスタム形式のバックアップをとる(初回はdbdump/postgresディレクトリを作成後実行)
# DBの接続情報は環境変数経由で指定
pg_logical_backup:
  pg_dump "-Fc" -h "${DSHACK_PG_HOST}" -p "${DSHACK_PG_PORT}" -U "${DSHACK_PG_USER}" -d "${DSHACK_PG_DBNAME}" > dbdump/postgres/dshack_devdb_$(shell date +"%Y%m%d").custom

# ダンプファイルのPathは、コマンドライン引数として与える(ex. make pg_all_restore DUMP_FILE_PATH="...")
pg_logical_restore:
  pg_restore -h ${DSHACK_PG_HOST} -p ${DSHACK_PG_PORT} -U ${DSHACK_PG_USER} -d ${DSHACK_PG_DBNAME} < ${DUMP_FILE_PATH}
```

バックアップは`make pg_logical_backup`、リストアは`make pg_logical_restore DUMP_FILE_PATH=<Path...>`により可能。

## ロギング環境

Fluend + kibana + ElasticSearchのロギング環境を`kubernetes/dshack-logging.yaml`に追加したが、PCスペック的に厳しいのでSkaffold.yamlの自動デプロイ対象外とし、ローカル開発では使用しないことに決定した。

ロギングには`./src/main/common/logger/common_logger.py`に含まれるCommonloggerクラスを使用する。

環境変数`APPLICATION_LOG_PATH`にログ出力フォルダを指定して実行する。

他にもプログラム中で使用するDB接続情報などは環境変数で与えるため、`.env`内に記載している環境変数を読み込んでプログラムを実行できる`forego`等のツールがローカル開発では便利。

```bash
brew install forego
```

## ソフトウェアテスト

テストライブラリとしてフィクスチャなどの機能が豊富なpytestを利用。DB絡みのテストにはテスト用のDBを使用する。パッケージのインストールもテストの実行もコンテナ上で走るため、環境構築は不要。カバレッジ測定を行うpytest-covを併用している。

TDDのプラクティスを採用し、ユニットテストとロジック実装とリファクタリングのサイクルを素早く回してソフトウェアの品質を高める。Skaffoldによるローカルでの自動テスト・自動デプロイが役立つ。

### 注意点

1. 実行速度が遅いテストは、開発サイクルを鈍らせる。そのためpytestのmark機能により、平常時に自動化するテストは制限する(スモークテスト)
2. 不要なテストはメンテンナンスするか削除する。後になってテストの意図・目的が分かるよう、最低限のコメントは残す。

テスト観点・テスト戦略については、ある程度開発を進めてみて決める。

## コーディングスタイル

- flake8

`flake8`を採用。`flake8`は、pep8・pyflakes・循環的複雑度のチェックからなるラッパーライブラリである。vscodeのコマンドパレットを開き、`Python: Select Linter`から`flake8`を選択することで有効化。

- numpydoc

docstringのスタイルとして`numpydoc`を採用。システムの重要な側面をモデル化したコアドキュメントと、統一的なdocstringのみを整備し、書き手・読み手それぞれにとって最低限のコストで、最新状態のシステムが理解できる状態を目指す。

(参考) [Python]可読性を上げるための、docstringの書き方を学ぶ（NumPyスタイル）[Qiitaリンク](https://qiita.com/simonritchie/items/49e0813508cad4876b5a)
