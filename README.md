# Data-infrastructure

当プロジェクトは、様々なデータ分析案件で利用できる分析システムの枠組みを作り上げることを最終目標としています。

**株価予測ダッシュボード**の構築という具体的なサンプルをもとに、分析用データベースの構築・データハンドリング・モデリング・API開発・ダッシュボード開発を行います。

## プロジェクトリポジトリ

- **data-infrastructure(Python)** : Web APIやクローリングによる分析用データベースの構築
- stochastic-modeling(Python) : データハンドリング、特徴量作成・モデリングを行い、株価予測モデルを構築
- stock-prediction-api(Go) : 株価予測ダッシュボードで利用するRestful APIのバックエンド実装
- stock-prediction-dashboard(TypeScript) : 株価予測ダッシュボードのフロントエンド実装

( )内は、主要な開発言語

![architecture](https://user-images.githubusercontent.com/56133802/76705546-2e361000-6724-11ea-83b7-664ca29465de.png)

## data-infrastructureリポジトリフォルダ構成

本リポジトリでは定期的に実行するバッチ処理がメインなので、扱うk8sリソースはJobまたはCronJobがメインです。

```tree
├── Dockerfile : ETLジョブやユニットテストを実行するためのDockerfile
├── alembic.ini : データベースマイグレーションパッケージalembicの設定ファイル
├── poetry.lock : パッケージの依存関係が記載されたlockファイル
├── pyproject.toml : パッケージのメタ情報・必要パッケージ等を含むファイル
├── skaffold.yaml : k8sのCI/CDツールとしてのskaffoldの設定ファイル
├── alembic
│   ├── env.py : alembic環境設定ファイル
│   └── versions : マイグレーションファイル本体
├── kubernetes
│   ├── cluster : clusterレベルのk8smanifestファイル(RBACやロギング関連)
│   ├── development : development環境用のk8smanifestファイル
│   ├── staging : staging環境用のk8smanifestファイル
│   └── production : production環境用のk8smanifestファイル
└── src
    ├── main
    │   ├── common
    │   │   ├── db : DB関連の共通処理
    │   │   └── logger : アプリケーション全体で使用するロガー
    │   └── stock : 株価取得ロジック
    │       ├── dto : SQL AlchemyのDTO
    │       └── main : 株価取得ロジックアプリケーション本体
    ├── shellscripts : バッチ処理や自動テストを行うシェルスクリプト(k8sのJob・CronJobで実行される)
    └── test
        ├── common : アプリケーション共通処理のユニットテスト
        ├── conftest.py : ユニットテスト全体で利用されるfixture等が定義されたファイル
        ├── pytest.ini : pytestの設定
        ├── resources : テスト用データ
        └── stock : 株価取得ロジックのユニットテスト
```

## Quick Start

本プロジェクトでは、開発環境・ステージング環境・本番環境全体を通してkubernetesを利用します。

ステージング環境・本番環境についてはGoogleCloudBuildにより、GithubのPullRequest時に自動テスト・クラウド上への自動デプロイを行います。

ここではローカルPCのminikubeで開発を始めるためのクイックスタートを記載します。インストール方法は環境により異なるのでリンク先の公式サイトを参照してください。

### 1. Dockerのインストール

Docker CEのインストール。Docker hubのアカウントを作成し、手順に従ってダウンロード&インストール。

- [Docker for Windows](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
- [Docker for Mac](https://hub.docker.com/editions/community/docker-ce-desktop-mac)

### 2. kubectlコマンドのインストール

kubectlコマンドは、k8sクラスタを操作するためのCLI。公式に沿ってインストール。

[kubernetes公式(kubectl)](https://kubernetes.io/ja/docs/tasks/tools/install-kubectl/)

（参考）mac OS

```bash
brew install kubernetes-cli
```

### 3. minikubeのインストール

ローカルで動作させるシングルノードのKubernetes。公式に沿ってインストール。

[kubernetes公式(minikube)](https://kubernetes.io/docs/tasks/tools/install-minikube/)

（参考）mac OS

```bash
brew cask install minikube
```

minikubeの起動は`minikube start`により行います。詰まった場合は、[kubernetes公式(minikube)](https://kubernetes.io/ja/docs/setup/learning-environment/minikube/)を参照してください。

### 4. skaffoldのインストール

Skaffoldはkubernetesを使ったアプリケーション開発において継続的デプロイをサポートするOSSです。 skaffold.yamlへ設定を記載することで、ローカル開発環境でも自動テストや必要なコンテナのデプロイを簡単に行うことができます。

[skaffold公式ドキュメント](https://skaffold.dev/docs/install/)

```bash
brew install skaffold
```

### 5. Pyenv + Poetryのインストール

本プロジェクトではパッケージマネージャとして、Pyenv + Poetryを利用しています。

コンテナ上で動作させる分には、ローカルPCの仮想環境は不要ですが、パッケージを追加する(poetry add)際などに無いと不便なのでインストールを推奨します。

Pythonのバージョンは3.7.6を利用します。

### 6. minikubeを起動する

`minikube start`により、ローカルのminikubeを起動しましょう。

`minikube status`でminikubeの起動状態が確認出来ます。

### 7. secret.yamlの作成

DBの認証情報など、秘匿情報はマニフェストファイル(secret.yaml)により管理しています。

[secret.yamlテンプレート](https://github.com/ds-hack/data-infrastructure/blob/master/kubernetes/development/secret.yaml.tmpl)に従って、DB名・ユーザー名・パスワードを設定しましょう。

Kubernetes Secretには、そのままの文字列ではなくbase64エンコーディングで加工後の文字列を格納します。

例として`dshack`をDB名としたい場合、

```bash
% echo -n "dshack" | base64 -
ZHNoYWNr
```

より、`ZHNoYWNr`の値をyamlに記載する必要があります。

### 8. skaffoldによるローカルデプロイの実行

ローカル開発で利用するコマンドは下記になります。

skaffoldはコンテナのビルド・タグ付け・デプロイのパイプラインを実行するため、ワンコマンドでデプロイすることが可能です。

- `skaffold run -p migrate` : DBコンテナを起動し、DTOクラスをもとに全テーブルを作成します。
- `skaffold dev -p sync-test` : pytestによる自動テストを実行します。`skaffold dev`はコンテナの影響範囲にあるファイル保存時に、コンテナの再ビルド〜デプロイを実施するので、継続的なユニットテストが可能です。
- `skaffold run` : 機能が完成し、ユニットテストにパスしたら`skaffold run`により、アプリケーションのデプロイを実行しましょう。

- 参考: Skaffold Pipelines

![workflow](https://user-images.githubusercontent.com/56133802/75913216-e1397a80-5e95-11ea-8e94-479eab9f645b.png)

個々のツールの使い方は、公式ドキュメントなどを参照いただければと思います。 (複数人開発になれば、簡単にwikiに使い方をまとめるかもしれません)

## データモデル

DBのドキュメンテーションに役立つ[SchemaSpy](http://schemaspy.org/)を活用しています。

[Github Pages(プロジェクトサイト)](https://ds-hack.github.io/data-infrastructure/index.html)で公開しています。

## システム構想・アーキテクチャ・コーディングスタイルなど

[プロジェクトWiki](https://github.com/ds-hack/data-infrastructure/wiki)に随時まとめていきます。

個人ブログ[DS Hack](https://datascientist-toolbox.com/)でも紹介予定です。
