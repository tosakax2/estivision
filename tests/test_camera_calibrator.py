import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import numpy as np
import cv2
from PySide6.QtCore import QCoreApplication
from estivision.camera.calibration import CameraCalibrator, CalibrationStatus


def test_calibrator_from_images(tmp_path):
    app = QCoreApplication([])
    calibrator = CameraCalibrator(board_size=(9, 6), square_size=1.0)

    class DummyWorker:
        def __init__(self):
            from PySide6.QtCore import Signal, QObject

            class _Obj(QObject):
                frame_ready = Signal(object)
            self.obj = _Obj()
            self.frame_ready = self.obj.frame_ready

    worker = DummyWorker()
    calibrator.start(worker)

    img = cv2.imread(str(Path(__file__).resolve().parents[1] / "images" / "chessboard_A4_9x6.png"))
    assert img is not None
    for _ in range(3):
        worker.frame_ready.emit(img)
        app.processEvents()

    # Wait for calibration thread
    while calibrator.status != CalibrationStatus.CALIBRATED:
        app.processEvents()

    assert calibrator.camera_matrix is not None
    assert calibrator.dist_coeffs is not None
