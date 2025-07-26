from pathlib import Path

import numpy as np
import pytest
from PySide6.QtCore import QCoreApplication
from PySide6.QtTest import QTest
from PySide6.QtGui import QImage

from estivision.pose.pose_preview_worker import PosePreviewWorker


@pytest.fixture(scope="module")
def app() -> QCoreApplication:  # type: ignore[override]
    return QCoreApplication([])


def test_pose_preview_worker_basic(app: QCoreApplication) -> None:
    model_path = Path("data/models/movenet_singlepose_lightning_v4.onnx")
    if not model_path.is_file():
        pytest.skip("モデルが見つからないためスキップ")

    worker = PosePreviewWorker(
        model_type="lightning",
        model_dir=model_path.parent,
        providers=["CPUExecutionProvider"],
    )
    results: list[QImage] = []
    worker.preview.connect(lambda img: results.append(img))
    worker.start()
    dummy = np.zeros((480, 640, 3), np.uint8)
    for _ in range(3):
        worker.enqueue_frame(dummy)
        QTest.qWait(100)
    worker.stop()
    assert results and all(isinstance(r, QImage) for r in results)

