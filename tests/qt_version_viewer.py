# ===== PySide6 バインディングのインポート =====
import PySide6
from PySide6.QtCore import qVersion, QLibraryInfo
# ====

def print_versions() -> None:
    """QtライブラリとPySide6バインディングのバージョンを表示する。"""
    # ===== Qtライブラリバージョン取得（qVersion使用） =====
    # --- qVersion()で現在のQtライブラリバージョンを取得 ---
    print(f"Qt ライブラリバージョン (qVersion): {qVersion()}")
    # ====

    # ===== Qtライブラリバージョン取得（QLibraryInfo使用） =====
    # --- QLibraryInfo.version()からバージョン文字列を生成 ---
    qt_ver: str = QLibraryInfo.version().toString()
    print(f"Qt ライブラリバージョン (QLibraryInfo): {qt_ver}")
    # ====

    # ===== PySide6バインディングバージョン取得 =====
    # --- PySide6.__version__からバインディングバージョンを取得 ---
    print(f"PySide6 バインディングバージョン: {PySide6.__version__}")
    # ====

# ===== エントリポイント =====
if __name__ == "__main__":
    # --- 直接実行された場合にバージョン表示関数を呼び出す ---
    print_versions()
# ====
