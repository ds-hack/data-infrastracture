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

システムが巨大化すると、主な動作環境をローカルからクラウドに移す可能性が高い。Immutableなコンテナ上での開発によりローカルからクラウドへの移行時、また開発メンバーの追加時に環境依存の障害を最小限にしたい。

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

## クラウドデプロイ

当分はローカルでの開発を予定している。アプリケーション公開時に記載。

## k8sアーキテクチャ

T.B.D

## データベース

ベースイメージは公式の`postgres:12.1`。本リポジトリは単純なCRUD処理がメインなので、SQLAlchemyのORM機能を使用している。

データベースの接続情報などの秘匿情報は、dshack-secret.yamlで管理し、内容はリポジトリ管理対象外とする。

テンプレートは`tmpl/dshack-secret.yaml.tmpl`を基に各自のローカルリポジトリで管理する。

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

## ロギング環境

T.B.D

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
