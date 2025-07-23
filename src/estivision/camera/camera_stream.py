# ===== 標準ライブラリ・外部ライブラリのインポート =====
from __future__ import annotations
import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
# =====


class CameraStream(QThread):
    """
    単一 VideoCapture から読み込んだフレームを複数処理系へ配信するハブスレッド。
    """

    # --- GUI プレビュー／処理用シグナル
    image_ready: Signal = Signal(QImage)
    frame_ready: Signal = Signal(object)  # ndarray (BGR)

    def __init__(self, device_id: int, fps: int = 30) -> None:
        """
        device_id で指定されたカメラを fps でストリーミングする。
        """
        super().__init__()
        # ===== 引数保持 =====
        self._device_id: int = device_id
        self._fps: int = fps
        self._running: bool = False
        # =====

    # ===== スレッド本体 =====
    def run(self) -> None:  # noqa: D401
        """
        VideoCapture を開き、フレーム取得ループを回す。
        """
        cap = cv2.VideoCapture(self._device_id, cv2.CAP_DSHOW)

        # --- カメラのデフォルト解像度
        default_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        default_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # --- 長辺 480px に縮小
        if default_w >= default_h:
            scale = 480 / default_w if default_w else 1
            target_w, target_h = 480, int(default_h * scale)
        else:
            scale = 480 / default_h if default_h else 1
            target_h, target_w = 480, int(default_w * scale)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  target_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, target_h)
        cap.set(cv2.CAP_PROP_FPS,          self._fps)

        self._running = cap.isOpened()
        if not self._running:
            return

        # --- 取得ループ
        while self._running:
            ret, frame = cap.read()
            if not ret:
                break

            # --- GUI 用 QImage 生成
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)

            # --- シグナル配信
            self.image_ready.emit(qimg)
            self.frame_ready.emit(frame)

            # --- FPS 制御
            self.msleep(int(1000 / self._fps))

        cap.release()
    # =====

    # ===== 停止要求 =====
    def stop(self) -> None:
        """
        取得ループを終了させる。
        """
        self._running = False
        self.wait()
    # =====
