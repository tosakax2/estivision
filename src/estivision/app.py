# ===== 標準ライブラリ・外部ライブラリのインポート =====
import sys
from PySide6.QtWidgets import QApplication
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
    # --- 直接実行された場合に main() を呼び出す
    main()
# =====
