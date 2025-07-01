import PySide6
from PySide6.QtCore import qVersion, QLibraryInfo


def print_versions() -> None:
    """
    Qt ライブラリと PySide6 バインディングのバージョンを表示する
    """
    # --- Qt ライブラリのバージョン取得（qVersion()）
    print(f"Qt ライブラリバージョン (qVersion): {qVersion()}")

    # --- Qt ライブラリのバージョン取得（QLibraryInfo）
    qt_ver = QLibraryInfo.version().toString()
    print(f"Qt ライブラリバージョン (QLibraryInfo): {qt_ver}")

    # --- PySide6 バインディングのバージョン
    print(f"PySide6 バインディングバージョン: {PySide6.__version__}")

if __name__ == "__main__":
    print_versions()
