# ===== インポート =====
from __future__ import annotations
import queue
from typing import Optional

import cv2                  as cv
import numpy                as np
from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtGui  import QImage

from .pose_estimator import PoseEstimator
from .drawing        import draw_pose
# ====

class PoseWorker(QThread):
    """CameraStream から送られたフレームで姿勢推定 → 骨格描画するスレッド。"""

    image_ready: Signal = Signal(QImage)     # GUI へ送る完成画像

    def __init__(
        self,
        *,
        model_type: str = "lightning",
        providers: Optional[list[str]] = None,
        thr: float = 0.2,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=20)
        self._running: bool = False
        self._est: PoseEstimator = PoseEstimator(model_type=model_type, providers=providers)
        self._thr = thr

    # CameraStream から呼ばれる slot
    def enqueue_frame(self, frame_bgr: np.ndarray) -> None:
        if not self._running:
            return
        try:
            self._queue.put_nowait(frame_bgr)
        except queue.Full:
            pass   # 最新フレーム優先で捨てる

    def run(self) -> None:  # noqa: D401
        self._running = True
        while self._running:
            try:
                frame = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            kps, scores = self._est.estimate(frame)
            drawn = draw_pose(frame, kps, scores, self._thr)

            rgb = cv.cvtColor(drawn, cv.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
            self.image_ready.emit(qimg)

    def stop(self) -> None:
        self._running = False
        self.requestInterruption()
        self.wait()
