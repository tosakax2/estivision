# ===== 標準ライブラリ・外部ライブラリのインポート =====
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
import qdarkstyle
# =====

# ===== 自作モジュールのインポート（相対パス） =====
from .gui.main_window import MainWindow
# =====

def main() -> None:
    """
    アプリケーションを初期化し、メインウィンドウを起動する。
    """
    # ===== QApplication の初期化 =====
    # --- コマンドライン引数を渡して QApplication インスタンスを生成
    app: QApplication = QApplication(sys.argv)

    # --- QDarkStyle のスタイルシートを適用
    style: str = qdarkstyle.load_stylesheet()
    app.setStyleSheet(style)

    # --- フォント設定
    font: QFont = QFont("Arial", 10)
    app.setFont(font)
    # =====

    # ===== メインウィンドウの生成・表示 =====
    # --- MainWindow クラスをインスタンス化
    window: MainWindow = MainWindow()

    # --- ウィンドウを画面に表示
    window.show()
    # =====

    # ===== イベントループ開始 =====
    # --- exec() で Qt のイベントループを実行し、終了コードを取得してプロセスを終了
    sys.exit(app.exec())
    # =====

# ===== エントリポイント =====
if __name__ == "__main__":
    main()
# =====
