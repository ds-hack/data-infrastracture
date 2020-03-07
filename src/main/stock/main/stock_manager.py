class StockManager(object):
    """
    pandas-datareaderを使って指定の銘柄コードに対する株価の情報を取得する。
    pandas-datareaderの最新のデータは翌立会日以降となるので、週末は基本的に木曜日までのデータしか存在しない。
    そこで、週末の最新データについては別途Webクローリングによって取得する。
    """
