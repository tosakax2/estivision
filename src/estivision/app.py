import sys
from PySide6.QtWidgets import QApplication

from .gui.main_window import MainWindow


def main():
    """
    アプリケーションを起動する
    """

    # --- QApplicationのインスタンスを生成
    app = QApplication(sys.argv)

    # --- メインウィンドウを作成して表示
    window = MainWindow()
    window.show()

    # --- アプリケーションのイベントループを開始
    sys.exit(app.exec())


# ===== エントリーポイント
if __name__ == "__main__":
    main()
