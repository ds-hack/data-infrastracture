/*
  masterデータのINSERT SQL (ホストからの実行コマンド)
  kubectl exec -it postgres-sts-0 -- psql -U <Username> -d <DBName> -c "$(cat db/stock-data.sql)"
*/
DELETE FROM company;
INSERT INTO company
    (company_id, company_name, stock_code, country_code, listed_market, foundation_date, longitude, latitude)
VALUES
    ('0001', '株式会社テクノプロ ', '6028', 'JP', '東証1部', '1997-06-01', 35.66, 139.73),
    ('0002', '株式会社ALBERT', '3906', 'JP', '東証マザーズ', '2005-07-01', 35.70, 139.69),
    ('0003', '株式会社KDDI', '9433', 'JP', '東証1部', '1984-06-01', 35.70, 139.75),
    ('0004', '株式会社NTTドコモ', '9437', 'JP', '東証1部', '1992-07-01', 35.67, 139.74)
;