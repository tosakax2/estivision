# ===== 標準ライブラリ・外部ライブラリのインポート =====
from __future__ import annotations

import sys
from typing import Callable, Optional
import cv2                              # OpenCV
import numpy as np                      # ndarray 型ヒント用
# =====

# ===== PySide6 モジュールのインポート =====
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QImage
# =====


class CameraCaptureWorker(QThread):
    """
    OpenCV でデバイスから連続フレームを読み込み、Signal で通知するスレッド。
    """

    # --- GUI プレビュー用 (QImage) と推論用 (np.ndarray BGR) をそれぞれ発行
    image_ready: Signal = Signal(QImage)
    frame_ready: Signal = Signal(object)   # ndarray を object で渡す

    def __init__(self, device_id: str | int, fps: int = 30) -> None:
        """キャプチャ用スレッドを初期化する。"""
        super().__init__()
        # ===== 引数保持 =====
        self._device_id = device_id
        self._fps: int = fps
        self._running: bool = False
        # =====

    # ===== スレッド本体 =====
    def run(self) -> None:  # noqa: D401
        """スレッド開始時に自動で呼ばれ、フレーム読み込みループを回す。"""
        # --- OpenCV VideoCapture を開く
        cap = cv2.VideoCapture(self._device_id, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)   # 必要に応じ調整
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS,          self._fps)

        self._running = cap.isOpened()
        if not self._running:
            return  # カメラが開けなかった場合は即終了

        # --- フレーム取得ループ
        while self._running:
            ret, frame = cap.read()
            if not ret:
                break

            # --- GUI 用に BGR → RGB → QImage へ変換
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            q_img = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)

            # --- シグナル送信（Qt スレッド間）
            self.image_ready.emit(q_img)     # プレビュー
            self.frame_ready.emit(frame)     # 姿勢推定用 (BGR ndarray)

            # --- FPS 制御：Qt のスリープを使う（ms 単位）
            self.msleep(int(1000 / self._fps))

        cap.release()
    # =====

    # ===== 外部停止リクエスト =====
    def stop(self) -> None:
        """キャプチャループを停止し、スレッド終了を要求する。"""
        self._running = False
        self.wait()  # スレッドが終了するまでブロック
    # =====
