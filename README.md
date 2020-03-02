# Data-infrastructure

個人分析用のデータ基盤(DW)構築用リポジトリ

当リポジトリ以外に、

- データハンドリング・MLモデル学習バッチを行うリポジトリ
- 各種サービスAPIを扱うリポジトリ
- Webアプリケーション・ダッシュボード等のプロダクトを扱うリポジトリ

を1つ以上作成する予定。

## システム構想

分析システムを作るモチベーションは、様々な種類のデータを収集し、分析し、場合によってはモデル構築し、可視化（予測）するまでの一連の工程を、拡張・再利用可能な形で残すことを主としている。

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

- Docker for Windows: https://hub.docker.com/editions/community/docker-ce-desktop-windows
- Docker for Mac: https://hub.docker.com/editions/community/docker-ce-desktop-mac

### kubectlコマンド

kubectlコマンドは、k8sクラスタを操作するためのCLI。公式に沿ってインストール。

- kubernetes公式(kubectl): https://kubernetes.io/ja/docs/tasks/tools/install-kubectl/

（参考）mac OS

```bash
brew install kubernetes-cli
```

### minikube

ローカルで動作させるシングルノードのKubernetes。公式に沿ってインストール。

- kubernetes公式(minikube): https://kubernetes.io/docs/tasks/tools/install-minikube/

（参考）mac OS

```bash
brew cask install minikube
# brew updade minikube  # update時
minikube start  # 仮想マシン起動
```

### skaffold

Skaffoldはkubernetesを使ったアプリケーション開発において継続的デプロイをサポートするOSS。リポジトリ直下のskaffold.yamlに設定を記載する。

- skaffold公式ドキュメント: https://skaffold.dev/docs/install/

```bash
brew install skaffold
```

## データベース

こちらもコンテナ化がまだなので、現状はローカルにpostgresql12.1をインストールしています。

本リポジトリは単純なCRUD処理がメインなので、SQLAlchemyのORM機能を使用しています。

データベースの接続情報はソースコードに直書きせず、トラッキング対象外の`.env`ファイルに下記のように記載してローカルで管理します。

```
POSTGRESQL_USER=*****
POSTGRESQL_PASSWORD=***********
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
・・・
```

テーブル作成は、`.env`ファイルの環境変数をロードした状態で`python ./src/migrate.py`により作成されます。

`forego`コマンドを使うとカレントディレクトリの`.env`を環境変数にロードして、

```
forego run python ./src/migrate.py
```

により楽に実行できます。

Macの場合、`brew install forego`でインストールできます。

**Docker導入時にインストール手順を更新します**

## ソフトウェアテスト

テストパッケージとして`fixture`等の便利機能が豊富な、`pytest`を使用しています。

データベース絡みのテストはテスト用DBを用意しています。

単体テスト・機能テストレベルで現状考えていることは、

- 実行速度が遅いテストはmark機能により、自動テストからは除外する
- テストの意図や目的を、テストメソッドのコメント等に残す
- 不要なテストはメンテナンスするか削除する
- テストカバレッジはあくまで指標であり、優先度次第では犠牲にする

などがあります。

テスト観点・テスト戦略については固まってからまとめたいと思います。

## コーディングスタイル

- flake8

`flake8`を採用しています。`flake8`は、pep8・pyflakes・循環的複雑度のチェックからなるラッパーライブラリです。

vscodeのコマンドパレットを開き、`Python: Select Linter`から`flake8`を選択することで有効化できます。

- 自己文書化 (docstringのすすめ)

`numpydoc`を採用しています。自己文書化のメリットとして、

1. 実装とドキュメントがセットになっていることで、古びたドキュメントのリスクが格段に減ること
2. コードの可読性が上がり、開発効率が上がること
3. コードからドキュメント生成が可能

引数や戻り値の情報以外に、オブジェクトの責務や、処理の目的といった設計時の観点をコメントに残しておくことが良いと思われます。

参考： [Python]可読性を上げるための、docstringの書き方を学ぶ（NumPyスタイル）　https://qiita.com/simonritchie/items/49e0813508cad4876b5a

