import os
import logging
from datetime import date


class CommonLogger(object):
    """
    アプリケーション全体で共通のログ形式を適用するため、ロガーを提供するクラス
    """
    def __init__(self):
        pass

    def get_application_logger(
        self,
        log_dir: str,
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
        # ファイルハンドラ
        log_name = f'application_log_{date.today().strftime("%Y%m%d")}.log'
        log_name = os.path.join(log_dir, log_name)
        fh = logging.FileHandler(log_name)
        # ログフォーマット
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        # ログレベルの設定
        logger.setLevel(log_level)

        return logger

    def get_sql_logger(
        self,
        log_dir: str,
        log_level: str,
    ):
        """
        SQL Alchemyで使用するロガークラス

        SQLログを出力したい場合に使用する

        Parameters
        ----------
        log_dir: str
            ログの出力先ディレクトリ
        log_level: str
            ロガーのログレベル

        Returns
        ----------
        logger: logging.Logger
            SQL Alchemyで使用するロガー
        """
        logger = logging.getLogger('sqlalchemy.engine')
        # ファイルハンドラ
        log_name = f'sql_log_{date.today().strftime("%Y%m%d")}.log'
        log_name = os.path.join(log_dir, log_name)
        fh = logging.FileHandler(log_name)
        logger.addHandler(fh)
        # ログフォーマット
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        # ログレベルの設定
        logger.setLevel(log_level)

        return logger
