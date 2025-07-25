# ===== インポート =====
# --- 標準ライブラリ ---
from __future__ import annotations
import queue
from pathlib import Path

# --- 外部ライブラリ ---
from typing import List, Tuple
import cv2
import numpy as np
from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtGui import QImage
# ====


class FrameCalibrator(QThread):
    """CameraStream から供給されるフレームを用いてキャリブレーションを実行するワーカ。"""

    # ===== 進捗／完了／失敗シグナル =====
    progress: Signal = Signal(int)       # 0–100 %
    finished: Signal = Signal(object)    # dict 結果
    failed: Signal = Signal(str)         # 失敗メッセージ
    preview: Signal = Signal(QImage)     # 処理中プレビュー
    capture_done: Signal = Signal()      # 解析用画像収集完了
    # =====

    def __init__(
        self,
        *,
        pattern_size: Tuple[int, int] = (9, 6),
        square_size: float = 20.0,
        samples: int = 20,
        device_id: int = 0,
        save_path: Path | None = None,
        parent: QObject | None = None
    ) -> None:
        """コンストラクタ。"""
        super().__init__(parent)
        # ===== 引数保持 =====
        self._pattern_size = pattern_size
        self._square_size = square_size
        self._samples = samples
        Path("data/parameters").mkdir(exist_ok=True)
        self._save_path = save_path or Path(f"data/parameters/calib_cam{device_id}.npz")
        # --- フレームバッファ ---
        self._queue: "queue.Queue[np.ndarray]" = queue.Queue(maxsize=100)
        self._running: bool = False
        # ====

    # ===== CameraStream から受信する slot =====
    def enqueue_frame(self, frame: np.ndarray) -> None:
        """外部からフレームを受信しキューに格納する。"""
        if not self._running:
            return
        try:
            self._queue.put_nowait(frame)
        except queue.Full:
            self._queue.get_nowait()      # 古いフレームを破棄
            self._queue.put_nowait(frame)

    # ===== スレッド本体 =====
    def run(self) -> None:  # noqa: D401
        """フレームを解析して規定枚数そろったら calibrateCamera を実行。"""
        self._running = True

        objp = self._create_object_points()
        obj_pts: List[np.ndarray] = []
        img_pts: List[np.ndarray] = []

        collected = 0
        while self._running and collected < self._samples:
            try:
                frame = self._queue.get(timeout=1.0)
            except queue.Empty:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(
                gray, self._pattern_size,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
            )
            disp = frame.copy()
            if found:
                cv2.drawChessboardCorners(disp, self._pattern_size, corners, found)
            if found:
                # --- サブピクセル精緻化 ---
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                sub = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

                img_pts.append(sub)
                obj_pts.append(objp)
                collected += 1
                self.progress.emit(int(collected / self._samples * 100))
            rgb = cv2.cvtColor(disp, cv2.COLOR_BGR2RGB)
            h, w, _ = rgb.shape
            qimg = QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888)
            self.preview.emit(qimg)

        if collected < self._samples:
            # ウィンドウクローズによる停止など、割り込み要求が入った場合は
            # エラー扱いとせず静かに終了する
            if self.isInterruptionRequested():
                return
            self.failed.emit("十分なサンプルが集まりませんでした。")
            return

        if collected >= self._samples:
            self.capture_done.emit()

        if self.isInterruptionRequested():
            return

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_pts, img_pts, gray.shape[::-1], None, None
        )

        if self.isInterruptionRequested():
            return
        if not ret:
            self.failed.emit("キャリブレーションに失敗しました。")
            return

        # --- キャリブレーション完了時の保存 ---
        np.savez(self._save_path, camera_matrix=mtx, dist_coeffs=dist, rvecs=rvecs, tvecs=tvecs, reprojection_error=ret)

        self.finished.emit({
            "camera_matrix": mtx,
            "dist_coeffs": dist,
            "reprojection_error": ret,
            "file": str(self._save_path)
        })

    # ===== 停止要求 =====
    def stop(self) -> None:
        """ワーカを停止する。"""
        self._running = False
        self.requestInterruption()
        self.wait()

    # ===== 内部ヘルパ =====
    def _create_object_points(self) -> np.ndarray:
        """チェスボード上の 3D 座標 (Z=0) を生成。"""
        objp = np.zeros((self._pattern_size[0] * self._pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self._pattern_size[0], 0:self._pattern_size[1]].T.reshape(-1, 2)
        objp *= self._square_size
        return objp
