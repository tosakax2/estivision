# ===== 標準ライブラリのインポート =====
from typing import Tuple, List, Callable, Any
from pathlib import Path
# =====

# ===== PySide6 ウィジェット関連のインポート =====
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLayout, QVBoxLayout,
    QHBoxLayout, QGroupBox, QComboBox, QScrollArea,
    QMessageBox, QPushButton, QProgressBar
)
# =====

# ===== PySide6 コア／GUI モジュールのインポート =====
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QCloseEvent
# =====

# ===== 自作モジュールのインポート（相対パス） =====
from .style_constants import (
    BACKGROUND_COLOR,
    TEXT_COLOR,
    WARNING_COLOR
)
from ..camera.camera_manager import QtCameraManager
from ..camera.camera_stream import CameraStream
from ..camera.frame_calibrator import FrameCalibrator
from .safe_widgets import SafeComboBox
# =====


def safe_disconnect(signal: object, slot: Callable[..., Any]) -> None:
    """Disconnect ``slot`` from ``signal`` ignoring any errors."""
    try:
        signal.disconnect(slot)
    except Exception:
        pass


class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウ。
    """

    # --------------------------------------------------------------------- #
    # コンストラクタ                                                         #
    # --------------------------------------------------------------------- #
    def __init__(self) -> None:
        """UI を構築し、カメラマネージャを初期化する。"""
        super().__init__()

        # ウィンドウタイトル
        self.setWindowTitle("ESTiVision")

        # --- カメラ別ウィジェット／スレッド管理辞書
        #     {cam_id: {...}}
        self.camera_widgets: dict[int, dict[str, object]] = {}
        self.streams: dict[int, CameraStream | None] = {1: None, 2: None}
        self.calib_workers: dict[int, FrameCalibrator | None] = {1: None, 2: None}
        self.preview_slots: dict[int, Callable[[QImage], None]] = {}

        # UI 構築
        self._setup_ui()

        # カメラ接続監視
        self.qt_cam_mgr: QtCameraManager = QtCameraManager()
        self.qt_cam_mgr.cameras_changed.connect(self._on_cameras_changed)

        # ウィンドウ幅をフィット
        self.adjustSize()
        self.setFixedWidth(self.width())

    # --------------------------------------------------------------------- #
    # UI 構築                                                                #
    # --------------------------------------------------------------------- #
    def _setup_ui(self) -> None:
        """
        スクロール対応コンテンツを中央に配置。
        """
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignTop)

        cameras_section = self._create_cameras_section()
        content_layout.addWidget(cameras_section)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll_area)

        # スクロールバー幅込みで最終幅を確定
        total_w = cameras_section.sizeHint().width() \
            + scroll_area.verticalScrollBar().sizeHint().width() + 24
        self.setFixedWidth(total_w)

    # --------------------------------------------------------------------- #
    # セクション生成                                                         #
    # --------------------------------------------------------------------- #
    def _create_cameras_section(self) -> QGroupBox:
        """
        カメラ 1・2 のプレビューグループを並べる。
        """
        layout = QHBoxLayout()
        for cam_id in (1, 2):
            grp, combo, label, calib_btn, status_lbl, progress = (
                self._create_camera_group(cam_id)
            )
            self.camera_widgets[cam_id] = {
                "combo": combo,
                "label": label,
                "calib_btn": calib_btn,
                "status": status_lbl,
                "progress": progress,
            }
            self.preview_slots[cam_id] = self._make_qimage_updater(label)
            layout.addWidget(grp)

        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        group = QGroupBox("Camera preview")
        group.setLayout(layout)
        return group

    def _create_camera_group(
        self,
        cam_id: int
    ) -> Tuple[QGroupBox, QComboBox, QLabel, QPushButton, QLabel, QProgressBar]:
        """
        cam_id 用の UI グループ生成。
        """
        combo = SafeComboBox()
        combo.addItem("未選択")
        combo.setFixedWidth(320)
        combo.currentIndexChanged.connect(
            lambda idx, cid=cam_id: self._on_camera_selected(cid, idx)
        )

        label = QLabel(f"Camera {cam_id} 未接続")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(320, 320)
        label.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {TEXT_COLOR};
            border-radius: 8px;
        """)

        calib_btn = QPushButton("キャリブレーション開始")
        calib_btn.setEnabled(False)
        calib_btn.clicked.connect(
            lambda _, cid=cam_id: self._on_calibration_start(cid)
        )

        status_lbl = QLabel("未キャリブレーション")
        status_lbl.setAlignment(Qt.AlignCenter)
        status_lbl.setStyleSheet(f"color: {WARNING_COLOR};")

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setFixedWidth(320)
        progress.setVisible(False)

        vbox = QVBoxLayout()
        vbox.addWidget(combo)
        vbox.addWidget(label)
        vbox.addWidget(calib_btn)
        vbox.addWidget(status_lbl)
        vbox.addWidget(progress)
        vbox.setSizeConstraint(QLayout.SetFixedSize)
        vbox.setContentsMargins(16, 16, 16, 8)

        group = QGroupBox(f"Camera {cam_id}")
        group.setLayout(vbox)
        return group, combo, label, calib_btn, status_lbl, progress

    def _make_qimage_updater(self, label: QLabel) -> Callable[[QImage], None]:
        """QImage をラベルへ描画するコールバックを生成。"""
        def _update(qimg: QImage) -> None:
            label.setPixmap(
                QPixmap.fromImage(qimg).scaled(
                    320,
                    320,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        return _update

    # --------------------------------------------------------------------- #
    # カメラリスト更新                                                       #
    # --------------------------------------------------------------------- #
    def _on_cameras_changed(self, names: List[str]) -> None:
        """
        デバイス接続変化時にコンボを更新。
        """
        for cam_id in (1, 2):
            combo: QComboBox = self.camera_widgets[cam_id]["combo"]  # type: ignore[index]
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("未選択")
            for n in names:
                combo.addItem(n)
            combo.blockSignals(False)
        self._update_combo_enabled_states()

    # --------------------------------------------------------------------- #
    # コンボ選択                                                             #
    # --------------------------------------------------------------------- #
    def _on_camera_selected(self, cam_id: int, index: int) -> None:
        """
        カメラ選択／解除時の処理。
        """
        widgets = self.camera_widgets[cam_id]
        combo: QComboBox = widgets["combo"]  # type: ignore[index]
        label: QLabel = widgets["label"]  # type: ignore[index]
        calib_btn: QPushButton = widgets["calib_btn"]  # type: ignore[index]
        status_lbl: QLabel = widgets["status"]  # type: ignore[index]
        progress: QProgressBar = widgets["progress"]  # type: ignore[index]
        other_combo: QComboBox = self.camera_widgets[2 if cam_id == 1 else 1]["combo"]  # type: ignore[index]
        update_slot = self.preview_slots[cam_id]
        stream: CameraStream | None = self.streams[cam_id]
        worker: FrameCalibrator | None = self.calib_workers[cam_id]

        # --- 既存ストリーム停止
        if stream:
            safe_disconnect(stream.image_ready, update_slot)
            stream.stop()
            self.streams[cam_id] = None

        # --- キャリブレーションワーカ停止
        if worker:
            if stream:
                safe_disconnect(stream.frame_ready, worker.enqueue_frame)
            safe_disconnect(worker.preview, update_slot)
            worker.stop()
            self.calib_workers[cam_id] = None
        label.clear()
        label.setText(f"Camera {cam_id} 未接続")
        progress.setVisible(False)
        progress.setValue(0)

        # --- ボタン／ステータス初期化
        calib_btn.setEnabled(False)
        status_lbl.setText("未キャリブレーション")
        status_lbl.setStyleSheet(f"color: {WARNING_COLOR};")
        status_lbl.setVisible(True)

        # --- 未選択
        if index == 0:
            self._update_combo_enabled_states()
            return

        device_id = index - 1
        # --- キャリブレーション済みかチェック
        npz_path = Path(f"data/calib_cam{device_id}.npz")
        if npz_path.exists():
            try:
                import numpy as np
                npz = np.load(npz_path)
                error = float(npz.get("reprojection_error", np.nan))
            except Exception:
                error = None
            self._set_calib_status_label(status_lbl, error)
        else:
            status_lbl.setStyleSheet(f"color: {WARNING_COLOR};")
            status_lbl.setTextFormat(Qt.PlainText)
            status_lbl.setText("未キャリブレーション")

        # --- 重複選択チェック
        if other_combo.currentIndex() == index:
            QMessageBox.warning(
                self, "カメラ重複",
                "そのカメラは既に別スロットで使用中です。"
            )
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)
            self._update_combo_enabled_states()
            return

        # --- 新ストリーム開始
        stream = CameraStream(device_id)
        stream.image_ready.connect(update_slot)
        stream.error.connect(lambda msg, cid=cam_id: self._on_stream_error(cid, msg))
        stream.start()
        self.streams[cam_id] = stream

        # --- ボタン有効化
        calib_btn.setEnabled(True)

        self._update_combo_enabled_states()
        self._refresh_calib_ui(cam_id)

    # --------------------------------------------------------------------- #
    # キャリブレーション開始                                                 #
    # --------------------------------------------------------------------- #
    def _on_calibration_start(self, cam_id: int) -> None:
        """
        キャリブレーションボタン押下時。
        """
        widgets = self.camera_widgets[cam_id]
        combo: QComboBox = widgets["combo"]  # type: ignore[index]
        calib_btn: QPushButton = widgets["calib_btn"]  # type: ignore[index]
        status_lbl: QLabel = widgets["status"]  # type: ignore[index]
        progress: QProgressBar = widgets["progress"]  # type: ignore[index]

        stream = self.streams[cam_id]
        worker = self.calib_workers[cam_id]
        update_slot = self.preview_slots[cam_id]

        if combo.currentIndex() == 0:
            return

        if worker:
            return

        calib_btn.setEnabled(False)
        status_lbl.setVisible(False)
        progress.setValue(0)
        progress.setVisible(True)

        device_id = combo.currentIndex() - 1
        calib_worker = FrameCalibrator(device_id=device_id)
        self.calib_workers[cam_id] = calib_worker

        if stream:
            stream.frame_ready.connect(calib_worker.enqueue_frame)
            safe_disconnect(stream.image_ready, update_slot)

        calib_worker.preview.connect(update_slot)

        calib_worker.progress.connect(progress.setValue)
        calib_worker.capture_done.connect(lambda cid=cam_id: self._on_capture_done(cid))
        calib_worker.finished.connect(lambda res, cid=cam_id: self._on_calibration_finished(cid, res))
        calib_worker.failed.connect(lambda msg, cid=cam_id: self._on_calibration_failed(cid, msg))

        calib_worker.start()

    def _on_capture_done(self, cam_id: int) -> None:
        """撮影終了時にプレビュー接続を戻す。"""
        stream = self.streams[cam_id]
        worker = self.calib_workers[cam_id]
        update_slot = self.preview_slots[cam_id]
        if stream and worker:
            stream.frame_ready.disconnect(worker.enqueue_frame)
            safe_disconnect(worker.preview, update_slot)
            stream.image_ready.connect(update_slot)

    def _on_calibration_finished(self, cam_id: int, result: dict[str, object]) -> None:
        """キャリブレーション完了時。"""
        widgets = self.camera_widgets[cam_id]
        status_lbl: QLabel = widgets["status"]  # type: ignore[index]
        calib_btn: QPushButton = widgets["calib_btn"]  # type: ignore[index]
        progress: QProgressBar = widgets["progress"]  # type: ignore[index]

        progress.setVisible(False)
        status_lbl.setVisible(True)
        error = result.get("reprojection_error", None)
        self._set_calib_status_label(status_lbl, error)

        calib_btn.setEnabled(True)

        worker = self.calib_workers[cam_id]
        if worker:
            worker.wait()
        self.calib_workers[cam_id] = None

    def _on_calibration_failed(self, cam_id: int, message: str) -> None:
        """キャリブレーション失敗時。"""
        widgets = self.camera_widgets[cam_id]
        status_lbl: QLabel = widgets["status"]  # type: ignore[index]
        calib_btn: QPushButton = widgets["calib_btn"]  # type: ignore[index]
        progress: QProgressBar = widgets["progress"]  # type: ignore[index]

        QMessageBox.critical(self, "キャリブレーション失敗", message)
        progress.setVisible(False)
        status_lbl.setVisible(True)
        status_lbl.setText("未キャリブレーション")
        status_lbl.setStyleSheet(f"color: {WARNING_COLOR};")
        calib_btn.setEnabled(True)

        worker = self.calib_workers[cam_id]
        if worker:
            worker.wait()
        self.calib_workers[cam_id] = None

    def _on_stream_error(self, cam_id: int, message: str) -> None:
        """CameraStream からのエラー受信時。"""
        QMessageBox.critical(self, "カメラ接続失敗", message)
        combo: QComboBox = self.camera_widgets[cam_id]["combo"]  # type: ignore[index]
        combo.blockSignals(True)
        combo.setCurrentIndex(0)
        combo.blockSignals(False)
        self._on_camera_selected(cam_id, 0)

    # --------------------------------------------------------------------- #
    # UI ヘルパ                                                              #
    # --------------------------------------------------------------------- #
    def _update_combo_enabled_states(self) -> None:
        """
        同じカメラの重複選択を防ぐため item の Enabled を切り替える。
        """
        combo1: QComboBox = self.camera_widgets[1]["combo"]  # type: ignore[index]
        combo2: QComboBox = self.camera_widgets[2]["combo"]  # type: ignore[index]
        sel1 = combo1.currentIndex()
        sel2 = combo2.currentIndex()

        for idx in range(combo1.count()):
            itm1 = combo1.model().item(idx)
            itm2 = combo2.model().item(idx)
            itm1.setEnabled(idx == 0 or idx != sel2)
            itm2.setEnabled(idx == 0 or idx != sel1)

    def _refresh_calib_ui(self, cam_id: int) -> None:
        """
        combo とワーカ状態からキャリブレーションボタンの Enabled を更新。
        """
        widgets = self.camera_widgets[cam_id]
        combo: QComboBox = widgets["combo"]  # type: ignore[index]
        calib_btn: QPushButton = widgets["calib_btn"]  # type: ignore[index]
        worker = self.calib_workers[cam_id]

        calib_btn.setEnabled(combo.currentIndex() != 0 and worker is None)
    
    def _set_calib_status_label(self, status_lbl: QLabel, error: float | None, threshold: float = 1.0) -> None:
        """
        キャリブレーション完了時または再選択時のステータスラベル表示を共通化する。
        """
        status_lbl.setStyleSheet("")  # 色指定リセット（qdarkstyleデフォルトに）
        from .style_constants import SUCCESS_COLOR, WARNING_COLOR
        if error is not None and not (isinstance(error, float) and (error != error)):  # NaN防止
            if error > threshold:
                error_color = WARNING_COLOR
            else:
                error_color = SUCCESS_COLOR
            msg = (
                "キャリブレーション完了<br>"
                "再投影誤差："
                f"<span style='color:{error_color}; font-weight:bold'>{error:.2f}px</span>"
            )
            status_lbl.setTextFormat(Qt.RichText)
            status_lbl.setText(msg)
        else:
            status_lbl.setTextFormat(Qt.PlainText)
            status_lbl.setText("キャリブレーション完了")

    # --------------------------------------------------------------------- #
    # ウィンドウクローズ                                                     #
    # --------------------------------------------------------------------- #
    def closeEvent(self, event: QCloseEvent) -> None:
        """
        すべてのスレッドを安全に停止。
        """
        for stream in self.streams.values():
            if stream:
                stream.stop()

        for worker in self.calib_workers.values():
            if worker:
                worker.requestInterruption()
                worker.stop()

        super().closeEvent(event)
