"""Worker thread for pose overlay preview."""

# ===== インポート =====
from __future__ import annotations
import queue
from pathlib import Path
from typing import List

import cv2 as cv
import numpy as np
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QImage

from .pose_estimator import PoseEstimator
from .drawing import draw_pose
# ====


class PosePreviewWorker(QThread):
    """Receive frames and emit pose overlay images."""

    preview: Signal = Signal(QImage)

    def __init__(
        self,
        model_type: str = "lightning",
        *,
        model_dir: Path | None = None,
        providers: List[str] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=5)
        self._running = False
        self._estimator = PoseEstimator(
            model_type=model_type,
            model_dir=model_dir,
            providers=providers,
        )

    def enqueue_frame(self, frame: np.ndarray) -> None:
        """Receive frame from CameraStream."""
        if not self._running:
            return
        try:
            self._queue.put_nowait(frame)
        except queue.Full:
            self._queue.get_nowait()
            self._queue.put_nowait(frame)

    def run(self) -> None:  # noqa: D401
        """Main loop processing frames."""
        self._running = True
        while self._running:
            try:
                frame = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue
            if self.isInterruptionRequested():
                break
            kps, scores = self._estimator.estimate(frame)
            drawn = draw_pose(frame, kps, scores)
            rgb = cv.cvtColor(drawn, cv.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
            self.preview.emit(qimg)

    def stop(self) -> None:
        """Stop worker thread."""
        self._running = False
        self.requestInterruption()
        self.wait()
