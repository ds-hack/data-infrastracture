import sys
import logging


class CommonLogger(object):
    """
    アプリケーション全体で共通のログ形式を適用するため、ロガーを提供するクラス

    ログはコンテナの標準出力に出力してfluentd等のagentにより集約することで、モニタリング・分析する。
    """
    def __init__(self):
        pass

    def get_application_logger(
        self,
        mod_name: str,
        log_level: str = 'INFO',
    ):
        """
        アプリケーションで使用するロガークラス

        ログを出力するモジュールからget_application_logger()を呼び出す形で使用

        Parameters
        ----------
        log_dir: str
            ログの出力先ディレクトリ
        mod_name: str
            ロガーを取得するモジュール名
        log_level: str
            ロガーのログレベル

        Returns
        ----------
        logger: logging.Logger
            アプリケーションで使用するロガー
            例) logger.warn('some log')
        """
        logger = logging.getLogger(mod_name)
        fh = logging.StreamHandler(sys.stdout)
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.setLevel(log_level)

        return logger
