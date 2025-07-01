# src/estivision/app.py

import sys
from PySide6.QtWidgets import QApplication

from .gui.main_window import MainWindow


def main() -> None:
    """
    アプリケーションを起動する
    """
    # --- QApplicationのインスタンスを生成
    app: QApplication = QApplication(sys.argv)

    # --- メインウィンドウを作成して表示
    window: MainWindow = MainWindow()
    window.show()

    # --- アプリケーションのイベントループを開始
    sys.exit(app.exec())


# ===== エントリーポイント
if __name__ == "__main__":
    main()
