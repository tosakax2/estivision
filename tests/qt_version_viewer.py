# ===== インポート =====
# --- 外部ライブラリ ---
import PySide6
from PySide6.QtCore import qVersion, QLibraryInfo
# ====


def print_versions() -> None:
    """QtライブラリとPySide6バインディングのバージョンを表示する。"""
    # --- qVersion()で現在のQtライブラリバージョンを取得 ---
    print(f"Qt ライブラリバージョン (qVersion)：{qVersion()}")

    # --- QLibraryInfo.version()からバージョン文字列を生成 ---
    qt_ver: str = QLibraryInfo.version().toString()
    print(f"Qt ライブラリバージョン (QLibraryInfo)：{qt_ver}")

    # --- PySide6.__version__からバインディングバージョンを取得 ---
    print(f"PySide6 バインディングバージョン：{PySide6.__version__}")


# ===== エントリポイント =====
if __name__ == "__main__":
    print_versions()
