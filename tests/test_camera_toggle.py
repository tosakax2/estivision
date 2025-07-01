# ===== 標準ライブラリのインポート =====
import os
import sys
import subprocess
import time
import threading
# ==========

# ===== モジュール検索パス設定 =====
# --- src/estivision をパスに追加（editable installしていない場合）
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
# ==========

# ===== 型ヒント用インポート =====
from typing import List
# ==========

# ===== PySide6 インポート =====
from PySide6.QtGui import QGuiApplication
# ==========

# ===== 自作モジュールインポート =====
from estivision.camera.camera_manager import QtCameraManager
# ==========

# ===== 定数定義 =====
# --- PowerShell で使用するカメラの InstanceId を設定
DEVICE_ID: str = r"USB\VID_04F2&PID_B7BA&MI_00\6&7BAC750&1&0000"
# ==========

def toggle_device() -> None:
    """
    内蔵カメラを無効化＆再有効化する。
    """
    # ===== デバイス無効化 =====
    # --- PowerShell で PnP デバイスを無効化し videoInputsChanged を促す
    subprocess.run([
        "powershell", "-Command",
        f"Disable-PnpDevice -InstanceId '{DEVICE_ID}' -Confirm:$false"
    ], check=True)
    # ==========

    # ===== ウェイト =====
    # --- 2秒間待機してデバイス状態の反映を待つ
    time.sleep(2)
    # ==========

    # ===== デバイス有効化 =====
    # --- PowerShell で PnP デバイスを再有効化
    subprocess.run([
        "powershell", "-Command",
        f"Enable-PnpDevice -InstanceId '{DEVICE_ID}' -Confirm:$false"
    ], check=True)
    # ==========

def on_cameras_changed(names: List[str]) -> None:
    """
    cameras_changed シグナル受信時のコールバック。
    """
    # ===== シグナル受信処理 =====
    # --- 更新されたカメラ名リストを出力
    print("🔄 cameras_changed:", names)
    # ==========

def main() -> None:
    """
    カメラ抜き差しテストを実行するメイン関数。
    """
    # ===== QGuiApplication 初期化 =====
    # --- GUI イベントループ用アプリケーションを生成
    app: QGuiApplication = QGuiApplication([])
    # ==========

    # ===== QtCameraManager セットアップ =====
    # --- カメラ接続検知マネージャを生成しシグナル接続
    manager: QtCameraManager = QtCameraManager()
    manager.cameras_changed.connect(on_cameras_changed)
    # ==========

    # ===== 初回デバイス一覧通知 =====
    # --- 確実に初期一覧を表示するため notify を直接呼び出し
    manager._notify()
    # ==========

    # ===== デバイス抜き差しトグル開始 =====
    # --- 別スレッドでデバイストグル処理を実行
    threading.Thread(target=toggle_device, daemon=True).start()
    # ==========

    # ===== テスト開始メッセージ =====
    # --- ユーザ提示用の案内メッセージを表示
    print("=== 内蔵カメラの抜き差しテスト中 ===")
    print("管理者権限で実行してください。Ctrl+Cで停止。")
    # ==========

    # ===== イベントループ実行 =====
    # --- Qt イベント処理と短時間スリープを繰り返し実行
    try:
        while True:
            app.processEvents()    # イベント処理を行い応答を維持
            time.sleep(0.5)        # CPU 使用率抑制のため待機
    except KeyboardInterrupt:
        # --- Ctrl+C 受信でループを抜け、テスト終了を出力
        print("\n=== テスト終了 ===")
    # ==========

# ===== エントリポイント =====
if __name__ == "__main__":
    # --- スクリプトとして実行された場合に main を呼び出す
    main()
# ==========
