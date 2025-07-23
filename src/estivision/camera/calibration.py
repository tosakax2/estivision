import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, QThread


class CalibrationStatus:
    NOT_CALIBRATED = "未キャリブレーション"
    CALIBRATING = "キャリブレーション中"
    CALIBRATED = "キャリブレーション完了"


class _CalibrationCompute(QThread):
    finished_with_result = Signal(object, object)

    def __init__(self, objpoints, imgpoints, image_size):
        super().__init__()
        self._objpoints = objpoints
        self._imgpoints = imgpoints
        self._image_size = image_size

    def run(self) -> None:  # noqa: D401
        """Run calibration in a worker thread."""
        _, mtx, dist, _, _ = cv2.calibrateCamera(
            self._objpoints, self._imgpoints, self._image_size, None, None
        )
        self.finished_with_result.emit(mtx, dist)


class CameraCalibrator(QObject):
    status_changed = Signal(str)

    def __init__(self, board_size=(9, 6), square_size=1.0):
        super().__init__()
        self.board_size = board_size
        self.square_size = square_size
        self.status = CalibrationStatus.NOT_CALIBRATED
        self.status_changed.emit(self.status)

        self._objpoints = []
        self._imgpoints = []
        self._required = 15
        self._frame_source = None
        self._image_size = None

    def start(self, frame_source, required_frames=15):
        self._objpoints = []
        self._imgpoints = []
        self._required = required_frames
        self._frame_source = frame_source
        self._image_size = None

        try:
            frame_source.frame_ready.disconnect(self._collect)
        except Exception:
            pass
        frame_source.frame_ready.connect(self._collect)

        self.status = CalibrationStatus.CALIBRATING
        self.status_changed.emit(self.status)

    def reset(self) -> None:
        if self._frame_source:
            try:
                self._frame_source.frame_ready.disconnect(self._collect)
            except Exception:
                pass
        self.status = CalibrationStatus.NOT_CALIBRATED
        self.status_changed.emit(self.status)

    def _collect(self, frame):
        if self.status != CalibrationStatus.CALIBRATING:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, self.board_size)
        if ret:
            criteria = (
                cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_MAX_ITER,
                30,
                0.001,
            )
            cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

            objp = np.zeros((self.board_size[0] * self.board_size[1], 3), np.float32)
            objp[:, :2] = (
                np.mgrid[0 : self.board_size[0], 0 : self.board_size[1]].T.reshape(-1, 2)
            )
            objp *= self.square_size

            self._imgpoints.append(corners)
            self._objpoints.append(objp)
            if self._image_size is None:
                self._image_size = gray.shape[::-1]

        if len(self._imgpoints) >= self._required:
            try:
                self._frame_source.frame_ready.disconnect(self._collect)
            except Exception:
                pass
            self._compute_thread = _CalibrationCompute(
                self._objpoints, self._imgpoints, self._image_size
            )
            self._compute_thread.finished_with_result.connect(self._on_finished)
            self._compute_thread.start()

    def _on_finished(self, cam_matrix, dist_coeffs):
        self.camera_matrix = cam_matrix
        self.dist_coeffs = dist_coeffs
        self.status = CalibrationStatus.CALIBRATED
        self.status_changed.emit(self.status)


