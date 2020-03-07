class StockManager(object):
    """
    pandas-datareaderを使って指定の銘柄コードに対する株価の情報を取得する。

    pandas-datareaderの最新のデータは翌立会日以降となるので、週末は基本的に木曜日までのデータしか存在しない。\n
    そこで、週末の最新データについては別途Webクローリングによって取得する。

    Attributes
    ----------
    stock_api: object
        pandas-datareaderを使用して、API経由で株価データを取得するクラス
    stock_crawler: object
        Webクローリングを利用して、Web上からデータを取得するクラス
    """
    def __init__(
        self,
        stock_api: object,
        stock_crawler: object
    ):
        """
        指定したStockAPIクラスとStockCrawlerクラスを使って株価データを取得する。

        インターフェース(抽象クラス)は定義せず、ダックタイピングを使用

        Parameters
        ----------
        stock_api: object
            pandas-datareaderを使用して、API経由で株価データを取得するクラス
        stock_crawler: object
            Webクローリングを利用して、Web上からデータを取得するクラス
        """
        self.stock_api = stock_api
        self.stock_crawler = stock_crawler

    def get_recent_date(
        self,
        stock_code: str,
    ):
        """
        """
