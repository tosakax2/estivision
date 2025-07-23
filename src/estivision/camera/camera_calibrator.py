# ===== 標準ライブラリのインポート =====
from __future__ import annotations
from pathlib import Path
from typing import List, Tuple
# =====

# ===== 外部ライブラリのインポート =====
import cv2
import numpy as np
# =====

# ===== PySide6 モジュールのインポート =====
from PySide6.QtCore import QThread, Signal
# =====


class CameraCalibrator(QThread):
    """
    チェスボードを用いた OpenCV カメラキャリブレーションワーカ。
    """

    # --- シグナル定義
    progress: Signal = Signal(int)       # 進捗率 (0–100)
    finished: Signal = Signal(object)    # 結果 dict
    failed: Signal = Signal(str)         # エラーメッセージ

    def __init__(
        self,
        device_id: int,
        *,
        pattern_size: Tuple[int, int] = (9, 6),   # 内側コーナー数
        square_size: float = 20.0,                # mm
        samples: int = 20,                        # 必要サンプル枚数
        save_path: Path | None = None,
        parent=None
    ) -> None:
        """コンストラクタ。"""
        super().__init__(parent)
        self.device_id = device_id
        self.pattern_size = pattern_size
        self.square_size = square_size
        self.samples = samples
        self.save_path = save_path or Path(f"calib_cam{device_id}.npz")

    # ===== スレッド本体 =====
    def run(self) -> None:  # noqa: D401
        """
        キャリブレーション処理を実行する。
        """
        cap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
        if not cap.isOpened():
            self.failed.emit("カメラが開けませんでした。")
            return

        objp: np.ndarray = self._create_object_points()
        obj_points: List[np.ndarray] = []
        img_points: List[np.ndarray] = []

        collected: int = 0
        while collected < self.samples:
            ret, frame = cap.read()
            if not ret:
                self.failed.emit("フレームを取得できませんでした。")
                cap.release()
                return

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            found, corners = cv2.findChessboardCorners(
                gray, self.pattern_size,
                cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE
            )

            if found:
                # --- 精緻化
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                corners_sub = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

                img_points.append(corners_sub)
                obj_points.append(objp)
                collected += 1

                # --- 進捗通知
                progress_pct: int = int(collected / self.samples * 100)
                self.progress.emit(progress_pct)

            # --- 取得速度抑制
            self.msleep(30)

        # --- キャリブレーション実行
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points, img_points, gray.shape[::-1], None, None
        )
        cap.release()

        if not ret:
            self.failed.emit("キャリブレーションに失敗しました。")
            return

        # --- 保存
        np.savez(
            self.save_path,
            camera_matrix=mtx,
            dist_coeffs=dist,
            rvecs=rvecs,
            tvecs=tvecs
        )

        # --- 完了通知
        self.finished.emit({
            "camera_matrix": mtx,
            "dist_coeffs": dist,
            "rvecs": rvecs,
            "tvecs": tvecs,
            "file": str(self.save_path)
        })

    # ===== オブジェクトポイント生成 =====
    def _create_object_points(self) -> np.ndarray:
        """
        チェスボード上の 3D 座標 (Z=0) を作成する。
        """
        objp = np.zeros((self.pattern_size[0] * self.pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[
            0:self.pattern_size[0],
            0:self.pattern_size[1]
        ].T.reshape(-1, 2)
        objp *= self.square_size  # mm 単位
        return objp

    # ===== 外部停止要求 =====
    def stop(self) -> None:
        """
        スレッドを強制停止する。
        """
        self.terminate()
        self.wait()
