import os
import sys
import subprocess
import time
import threading

# --- src/estivision をパスに追加（editable install していない場合）
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from PySide6.QtGui import QGuiApplication
from estivision.camera.camera_manager import QtCameraManager


# --- ここに PowerShell で取得した InstanceId をセット
DEVICE_ID = r"USB\VID_04F2&PID_B7BA&MI_00\6&7BAC750&1&0000"


def toggle_device():
    """
    内蔵カメラを無効化→有効化して
    Qt の videoInputsChanged イベントを発生させる
    """
    # --- 無効化
    subprocess.run([
        "powershell", "-Command",
        f"Disable-PnpDevice -InstanceId '{DEVICE_ID}' -Confirm:$false"
    ], check=True)

    # --- 少し待ってから再有効化
    time.sleep(2)

    # --- 有効化
    subprocess.run([
        "powershell", "-Command",
        f"Enable-PnpDevice -InstanceId '{DEVICE_ID}' -Confirm:$false"
    ], check=True)


def on_cameras_changed(names):
    """
    cameras_changed シグナル受信時のコールバック
    """
    print("🔄 cameras_changed:", names)


def main():
    # --- Qt の GUI 系アプリケーション初期化
    app = QGuiApplication([])

    # --- カメラマネージャ生成＆シグナル接続
    manager = QtCameraManager()
    manager.cameras_changed.connect(on_cameras_changed)

    # --- 初回一覧を確実に出力
    manager._notify()

    # --- 抜き差しトグルを別スレッドで実行
    threading.Thread(target=toggle_device, daemon=True).start()

    print("=== 内蔵カメラの抜き差しテスト中 ===")
    print("管理者権限で実行してください。Ctrl+Cで停止。")

    try:
        while True:
            app.processEvents()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n=== テスト終了 ===")


if __name__ == "__main__":
    main()
