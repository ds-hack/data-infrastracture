# Github Syncによりgh-pagesディレクトリ下をgh-pagesブランチのHEADに同期させる
java -jar schemaspy-6.1.0.jar
cd gh-pages
git add .
git commit -m "job: Update schamaspy datamodels."
git push origin gh-pages
