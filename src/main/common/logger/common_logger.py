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
        # ディレクトリが存在しない場合、作成する
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_name = f'application_log_{date.today().strftime("%Y%m%d")}.log'
        log_path = os.path.join(log_dir, log_name)

        logger = logging.getLogger(mod_name)
        # ファイルハンドラ
        fh = logging.FileHandler(log_path)
        # ログフォーマット
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        # ログレベルの設定
        logger.setLevel(log_level)

        return logger
