from typing import List
from PySide6.QtCore import QObject, Signal
from PySide6.QtMultimedia import QMediaDevices


class QtCameraManager(QObject):
    """
    QtMultimedia の QMediaDevices インスタンスを使って
    カメラデバイスの接続／切断を監視するクラス
    """
    # --- List[str] のカメラ名リストを通知
    cameras_changed: Signal = Signal(list)


    def __init__(self) -> None:
        """
        QMediaDevices の videoInputsChanged シグナルを監視して初期一覧を通知する
        """
        super().__init__()

        # ===== QMediaDevices インスタンス化
        # --- デバイス一覧変更イベントを受け取るためのメディアデバイスオブジェクト
        self._media_dev = QMediaDevices()

        # --- シグナル接続（引数なし／あり、どちらでも吸収）
        self._media_dev.videoInputsChanged.connect(self._on_devices_changed)

        # ===== 初回デバイス一覧取得
        # --- 現在接続中のデバイス一覧を取得
        self._devices = self._media_dev.videoInputs()
        
        # --- 初期一覧を通知
        self._notify()


    def _on_devices_changed(self, *args) -> None:
        """
        デバイス接続／切断検知時のコールバック
        （シグナルが引数なしでも *args で吸収可能）
        """
        # ===== デバイス一覧再取得
        # --- 最新のデバイス一覧を取得
        self._devices = self._media_dev.videoInputs()

        # --- 再通知
        self._notify()


    def _notify(self) -> None:
        """
        現在のデバイス名一覧を Signal で送出する
        """
        # ===== デバイス名抽出
        names: List[str] = [dev.description() for dev in self._devices]

        # --- シグナル発行
        self.cameras_changed.emit(names)


    def device_ids(self) -> List[str]:
        """
        内部識別子（deviceId）の一覧を返す
        """
        # ===== deviceId 抽出
        return [dev.deviceId() for dev in self._devices]


    def device_count(self) -> int:
        """
        接続中のカメラ台数を返す
        """
        # ===== 台数カウント
        return len(self._devices)
