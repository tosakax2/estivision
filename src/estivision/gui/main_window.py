# ===== 標準ライブラリのインポート =====
from typing import Tuple, List
from pathlib import Path
# =====

# ===== PySide6 ウィジェット関連のインポート =====
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLayout, QVBoxLayout,
    QHBoxLayout, QGroupBox, QComboBox, QScrollArea,
    QMessageBox, QPushButton
)
# =====

# ===== PySide6 コア／GUI モジュールのインポート =====
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
# =====

# ===== 自作モジュールのインポート（相対パス） =====
from .style_constants import BACKGROUND_COLOR, FOREGROUND_COLOR, PRIMARY_COLOR
from ..camera.camera_manager import QtCameraManager
from ..camera.camera_stream import CameraStream
from ..camera.frame_calibrator import FrameCalibrator
from .safe_widgets import SafeComboBox
# =====


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

        # UI 構築
        self._setup_ui()

        # カメラ接続監視
        self.qt_cam_mgr: QtCameraManager = QtCameraManager()
        self.qt_cam_mgr.cameras_changed.connect(self._on_cameras_changed)

        # ストリーム／キャリブレータ保持
        self.cam1_stream: CameraStream | None = None
        self.cam2_stream: CameraStream | None = None
        self.calib1_worker: FrameCalibrator | None = None
        self.calib2_worker: FrameCalibrator | None = None

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
        (grp1, self.camera1_combo, self.camera1_label, self.calib1_btn, self.calib1_status) = self._create_camera_group(1)

        (grp2, self.camera2_combo, self.camera2_label, self.calib2_btn, self.calib2_status) = self._create_camera_group(2)

        layout = QHBoxLayout()
        layout.addWidget(grp1)
        layout.addWidget(grp2)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        group = QGroupBox("Camera preview")
        group.setLayout(layout)
        return group

    def _create_camera_group(
        self,
        cam_id: int
    ) -> Tuple[QGroupBox, QComboBox, QLabel, QPushButton, QLabel]:
        """
        cam_id 用の UI グループ生成。
        """
        combo = SafeComboBox()
        combo.addItem("未選択")
        combo.setFixedWidth(480)
        combo.currentIndexChanged.connect(
            lambda idx, cid=cam_id: self._on_camera_selected(cid, idx)
        )

        label = QLabel(f"Camera {cam_id} 未接続")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(480, 480)
        label.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {FOREGROUND_COLOR};
            border-radius: 8px;
        """)

        calib_btn = QPushButton("キャリブレーション開始")
        calib_btn.setEnabled(False)
        calib_btn.clicked.connect(
            lambda _, cid=cam_id: self._on_calibration_start(cid)
        )

        status_lbl = QLabel("未キャリブレーション")
        status_lbl.setAlignment(Qt.AlignCenter)
        status_lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")

        vbox = QVBoxLayout()
        vbox.addWidget(combo)
        vbox.addWidget(label)
        vbox.addWidget(calib_btn)
        vbox.addWidget(status_lbl)
        vbox.setSizeConstraint(QLayout.SetFixedSize)
        vbox.setContentsMargins(16, 16, 16, 16)

        group = QGroupBox(f"Camera {cam_id}")
        group.setLayout(vbox)
        return group, combo, label, calib_btn, status_lbl

    # --------------------------------------------------------------------- #
    # カメラリスト更新                                                       #
    # --------------------------------------------------------------------- #
    def _on_cameras_changed(self, names: List[str]) -> None:
        """
        デバイス接続変化時にコンボを更新。
        """
        for combo in (self.camera1_combo, self.camera2_combo):
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
        combo = self.camera1_combo if cam_id == 1 else self.camera2_combo
        label = self.camera1_label if cam_id == 1 else self.camera2_label
        calib_btn = self.calib1_btn if cam_id == 1 else self.calib2_btn
        status_lbl = self.calib1_status if cam_id == 1 else self.calib2_status
        attr_stream = "cam1_stream" if cam_id == 1 else "cam2_stream"
        other_combo = self.camera2_combo if cam_id == 1 else self.camera1_combo

        # --- 既存ストリーム停止
        stream: CameraStream | None = getattr(self, attr_stream)
        if stream:
            stream.stop()
            setattr(self, attr_stream, None)
        label.clear()
        label.setText(f"Camera {cam_id} 未接続")

        # --- ボタン／ステータス初期化
        calib_btn.setEnabled(False)
        status_lbl.setText("未キャリブレーション")

        # --- 未選択
        if index == 0:
            self._update_combo_enabled_states()
            return

        device_id = index - 1
        # --- キャリブレーション済みかチェック
        npz_path = Path(f"data/calib_cam{device_id}.npz")
        if npz_path.exists():
            status_lbl.setText("キャリブレーション完了")
        else:
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
        stream.image_ready.connect(
            lambda qimg, lbl=label: lbl.setPixmap(
                QPixmap.fromImage(qimg).scaled(
                    480, 480, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        )
        stream.start()
        setattr(self, attr_stream, stream)

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
        combo = self.camera1_combo if cam_id == 1 else self.camera2_combo
        calib_btn = self.calib1_btn if cam_id == 1 else self.calib2_btn
        status_lbl = self.calib1_status if cam_id == 1 else self.calib2_status
        attr_stream = "cam1_stream" if cam_id == 1 else "cam2_stream"
        attr_worker = "calib1_worker" if cam_id == 1 else "calib2_worker"

        # --- 未選択チェック
        if combo.currentIndex() == 0:
            return

        # --- 既存ワーカ稼働中なら無視
        if getattr(self, attr_worker):
            return

        # --- UI 更新
        calib_btn.setEnabled(False)
        status_lbl.setText("キャリブレーション中...")

        # --- ワーカ生成
        device_id = combo.currentIndex() - 1
        calib_worker = FrameCalibrator(device_id=device_id)
        setattr(self, attr_worker, calib_worker)

        # --- ストリームからフレームを受信
        stream: CameraStream = getattr(self, attr_stream)
        stream.frame_ready.connect(calib_worker.enqueue_frame)

        # --- シグナル接続
        calib_worker.progress.connect(
            lambda p, lbl=status_lbl: lbl.setText(f"キャリブレーション中... ({p}%)")
        )
        calib_worker.finished.connect(
            lambda res, lbl=status_lbl, btn=calib_btn,
            worker_attr=attr_worker, strm=stream:
                self._on_calibration_finished(lbl, btn, worker_attr, strm, res)
        )
        calib_worker.failed.connect(
            lambda msg, lbl=status_lbl, btn=calib_btn,
            worker_attr=attr_worker, strm=stream:
                self._on_calibration_failed(lbl, btn, worker_attr, strm, msg)
        )

        calib_worker.start()

    def _on_calibration_finished(
        self,
        status_lbl: QLabel,
        calib_btn: QPushButton,
        worker_attr: str,
        stream: CameraStream,
        result: object
    ) -> None:
        """
        キャリブレーション完了時。
        """
        status_lbl.setText("キャリブレーション完了")
        calib_btn.setEnabled(True)

        # --- ストリームとの接続解除
        stream.frame_ready.disconnect(getattr(self, worker_attr).enqueue_frame)  # type: ignore[arg-type]

        # --- ワーカ破棄
        setattr(self, worker_attr, None)

    def _on_calibration_failed(
        self,
        status_lbl: QLabel,
        calib_btn: QPushButton,
        worker_attr: str,
        stream: CameraStream,
        message: str
    ) -> None:
        """
        キャリブレーション失敗時。
        """
        QMessageBox.critical(self, "キャリブレーション失敗", message)
        status_lbl.setText("未キャリブレーション")
        calib_btn.setEnabled(True)

        # --- ストリームとの接続解除
        stream.frame_ready.disconnect(getattr(self, worker_attr).enqueue_frame)  # type: ignore[arg-type]

        # --- ワーカ破棄
        setattr(self, worker_attr, None)

    # --------------------------------------------------------------------- #
    # UI ヘルパ                                                              #
    # --------------------------------------------------------------------- #
    def _update_combo_enabled_states(self) -> None:
        """
        同じカメラの重複選択を防ぐため item の Enabled を切り替える。
        """
        sel1 = self.camera1_combo.currentIndex()
        sel2 = self.camera2_combo.currentIndex()

        for idx in range(self.camera1_combo.count()):
            itm1 = self.camera1_combo.model().item(idx)
            itm2 = self.camera2_combo.model().item(idx)
            itm1.setEnabled(idx == 0 or idx != sel2)
            itm2.setEnabled(idx == 0 or idx != sel1)

    def _refresh_calib_ui(self, cam_id: int) -> None:
        """
        combo とワーカ状態からキャリブレーションボタンの Enabled を更新。
        """
        combo = self.camera1_combo if cam_id == 1 else self.camera2_combo
        calib_btn = self.calib1_btn if cam_id == 1 else self.calib2_btn
        worker = self.calib1_worker if cam_id == 1 else self.calib2_worker

        calib_btn.setEnabled(combo.currentIndex() != 0 and worker is None)

    # --------------------------------------------------------------------- #
    # ウィンドウクローズ                                                     #
    # --------------------------------------------------------------------- #
    def closeEvent(self, event) -> None:  # type: ignore[override]
        """
        すべてのスレッドを安全に停止。
        """
        for stream in (self.cam1_stream, self.cam2_stream):
            if stream:
                stream.stop()

        for worker in (self.calib1_worker, self.calib2_worker):
            if worker:
                worker.stop()

        super().closeEvent(event)
