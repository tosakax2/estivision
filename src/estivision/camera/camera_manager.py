# ===== 標準ライブラリのインポート =====
from typing import List
# =====

# ===== PySide6 コアモジュールのインポート =====
from PySide6.QtCore import QObject, Signal, QTimer
# =====

# ===== PySide6 マルチメディアモジュールのインポート =====
from PySide6.QtMultimedia import QMediaDevices, QCameraDevice
# =====


class QtCameraManager(QObject):
    """
    QtMultimedia の QMediaDevices を用いてカメラデバイスの接続／切断を監視するクラス
    """

    # --- List[str] のカメラ名リストを通知
    cameras_changed: Signal = Signal(list)

    def __init__(self) -> None:
        """
        シグナル接続および初回デバイス一覧通知を行う初期化処理。
        """
        super().__init__()

        # ===== QMediaDevices インスタンス生成とシグナル接続 =====
        # --- QMediaDevices からビデオ入力デバイス情報を取得
        self._media_dev: QMediaDevices = QMediaDevices()
        # --- デバイス変更時に _on_devices_changed を呼び出す
        self._media_dev.videoInputsChanged.connect(self._on_devices_changed)
        # =====

        # ===== 初期デバイス一覧取得 =====
        # --- 現在接続中の QCameraDevice オブジェクト一覧をキャッシュ
        self._devices: List[QCameraDevice] = self._media_dev.videoInputs()
        # =====

        # ===== 初回通知を次のイベントループで emit =====
        # --- シグナル接続後に必ず届くよう、0ms 後に呼び出しをスケジュール
        QTimer.singleShot(0, self._notify)
        # =====

    def _on_devices_changed(self, *args) -> None:
        """
        デバイスの接続／切断を検知し、キャッシュ更新および通知を行うハンドラ。
        """
        # ===== デバイスリスト更新 =====
        # --- 最新のビデオ入力デバイス一覧を再取得
        self._devices = self._media_dev.videoInputs()
        # =====

        # ===== 変更通知 =====
        # --- 更新後のデバイス名リストを emit
        self._notify()
        # =====

    def _notify(self) -> None:
        """
        現在接続中のカメラ名一覧を cameras_changed シグナルで通知する。
        """
        # ===== デバイス名リスト生成 =====
        # --- 各 QCameraDevice の description() をリスト化
        device_names: List[str] = [dev.description() for dev in self._devices]
        # =====

        # ===== シグナル送信 =====
        # --- cameras_changed シグナルでデバイス名一覧を通知
        self.cameras_changed.emit(device_names)
        # =====

    def device_ids(self) -> List[str]:
        """
        接続中カメラの内部デバイスID(deviceId)一覧を返す。
        """
        # ===== deviceId 抽出 =====
        # --- 各 QCameraDevice から deviceId() を取得
        return [dev.deviceId() for dev in self._devices]

    def device_count(self) -> int:
        """
        接続中カメラの台数を返す。
        """
        # ===== 台数取得 =====
        # --- デバイスリストの長さを返却
        return len(self._devices)

    def device_names(self) -> List[str]:
        """
        接続中カメラの description 一覧を返す。
        """
        # ===== description 抽出 =====
        # --- 各 QCameraDevice の description() を取得
        return [dev.description() for dev in self._devices]

    def devices(self) -> List[QCameraDevice]:
        """
        接続中の QCameraDevice オブジェクト一覧を返す。
        """
        # ===== オブジェクト一覧返却 =====
        # --- list() でコピーしたリストを返却
        return list(self._devices)
