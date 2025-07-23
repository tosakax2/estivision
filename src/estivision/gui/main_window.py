# ===== 標準ライブラリのインポート =====
from typing import Tuple, List
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
# --- GUI のスタイル定義（色定数）
from .style_constants import BACKGROUND_COLOR, FOREGROUND_COLOR, PRIMARY_COLOR
# --- カメラ接続監視用マネージャ
from ..camera.camera_manager import QtCameraManager
# --- OpenCV キャプチャ用ワーカ
from ..camera.camera_capture import CameraCaptureWorker
# --- キャリブレーション用ワーカ
from ..camera.camera_calibrator import CameraCalibrator
# =====


class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウを表すクラス
    """

    def __init__(self) -> None:
        """メインウィンドウを初期化し、UI を構築する。"""
        super().__init__()

        # ===== ウィンドウタイトル設定 =====
        # --- アプリ名をタイトルバーに表示
        self.setWindowTitle("ESTiVision")
        # =====

        # ===== UI 構築 =====
        # --- レイアウトやウィジェットを初期化
        self._setup_ui()
        # =====

        # ===== カメラ監視マネージャの初期化とシグナル接続 =====
        # --- 接続／切断の変化を受け取ってコンボを更新する
        self.qt_cam_mgr: QtCameraManager = QtCameraManager()
        self.qt_cam_mgr.cameras_changed.connect(self._on_cameras_changed)
        # =====

        # ===== キャプチャ・キャリブレーションワーカの保持用 =====
        self.cam1_worker: CameraCaptureWorker | None = None
        self.cam2_worker: CameraCaptureWorker | None = None
        self.calib1_worker: CameraCalibrator | None = None
        self.calib2_worker: CameraCalibrator | None = None
        # =====

        # ===== ウィンドウ幅を中身にフィットさせ固定 =====
        # --- サイズ計算後、横幅のみ固定
        self.adjustSize()
        self.setFixedWidth(self.width())
        # =====

    # ===== UI 初期化処理 =====
    def _setup_ui(self) -> None:
        """
        中央ウィジェットにスクロール対応のコンテンツをセットアップする。
        """
        # ===== コンテンツウィジェットとレイアウトの生成 =====
        content_widget: QWidget = QWidget()
        content_layout: QVBoxLayout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignTop)
        # =====

        # ===== カメラ選択セクションの追加 =====
        cameras_section: QGroupBox = self._create_cameras_section()
        content_layout.addWidget(cameras_section)
        # =====

        # ===== スクロールエリアの生成と設定 =====
        scroll_area: QScrollArea = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll_area)
        # =====

        # ===== ウィンドウ幅の最終調整 =====
        content_width: int = cameras_section.sizeHint().width()
        scroll_bar_width: int = scroll_area.verticalScrollBar().sizeHint().width()
        total_width: int = content_width + scroll_bar_width + 24
        self.adjustSize()
        self.setFixedWidth(total_width)
        # =====

    # ===== カメラセクションの作成 =====
    def _create_cameras_section(self) -> QGroupBox:
        """
        複数カメラのプレビュー用グループを横並びにまとめたセクションを返す。
        """
        (camera1_group, self.camera1_combo, self.camera1_label, self.calib1_btn, self.calib1_status) = self._create_camera_group(1)

        (camera2_group, self.camera2_combo, self.camera2_label, self.calib2_btn, self.calib2_status) = self._create_camera_group(2)

        layout: QHBoxLayout = QHBoxLayout()
        layout.addWidget(camera1_group)
        layout.addWidget(camera2_group)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)

        group: QGroupBox = QGroupBox("Camera preview")
        group.setLayout(layout)
        return group

    # ===== 個別カメラグループの作成 =====
    def _create_camera_group(
        self, camera_id: int
    ) -> Tuple[QGroupBox, QComboBox, QLabel, QPushButton, QLabel]:
        """
        指定 ID のカメラ用コンボボックスと映像表示ラベルを含むグループを生成する。
        """
        # --- デバイス選択コンボ
        combo: QComboBox = QComboBox()
        combo.addItem("未選択")
        combo.setFixedWidth(480)
        combo.currentIndexChanged.connect(
            lambda idx, cid=camera_id: self._on_camera_selected(cid, idx)
        )

        # --- プレビュー表示ラベル
        label: QLabel = QLabel(f"Camera {camera_id} 未接続")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(480, 480)
        label.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {FOREGROUND_COLOR};
            border-radius: 8px;
        """)

        # --- キャリブレーション開始ボタン
        calib_btn: QPushButton = QPushButton("キャリブレーション開始")
        calib_btn.setEnabled(False)  # 未選択時は無効化
        calib_btn.clicked.connect(
            lambda _, cid=camera_id: self._on_calibration_start(cid)
        )

        # --- キャリブレーションステータスラベル
        status_lbl: QLabel = QLabel("未キャリブレーション")
        status_lbl.setAlignment(Qt.AlignCenter)
        status_lbl.setStyleSheet(f"color: {PRIMARY_COLOR};")

        # --- レイアウト構築
        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(combo)
        layout.addWidget(label)
        layout.addWidget(calib_btn)
        layout.addWidget(status_lbl)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.setContentsMargins(16, 16, 16, 16)

        group: QGroupBox = QGroupBox(f"Camera {camera_id}")
        group.setLayout(layout)
        return group, combo, label, calib_btn, status_lbl

    # ===== カメラ一覧更新ハンドラ =====
    def _on_cameras_changed(self, device_names: List[str]) -> None:
        """
        カメラ接続状態の変化時にコンボボックスを更新する。
        """
        for combo in (self.camera1_combo, self.camera2_combo):
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("未選択")
            for name in device_names:
                combo.addItem(name)
            combo.blockSignals(False)

        # --- 選択済み重複の Enabled 状態更新
        self._update_combo_enabled_states()

    # ===== カメラ選択ハンドラ =====
    def _on_camera_selected(self, cam_id: int, index: int) -> None:
        """
        コンボボックスでカメラが選択／未選択になったときの処理。
        """
        # --- ターゲット UI を決定
        combo = self.camera1_combo if cam_id == 1 else self.camera2_combo
        label = self.camera1_label if cam_id == 1 else self.camera2_label
        calib_btn = self.calib1_btn if cam_id == 1 else self.calib2_btn
        status_lbl = self.calib1_status if cam_id == 1 else self.calib2_status
        attr_worker = "cam1_worker" if cam_id == 1 else "cam2_worker"
        other_combo = self.camera2_combo if cam_id == 1 else self.camera1_combo

        # --- 既存プレビュー停止
        worker: CameraCaptureWorker | None = getattr(self, attr_worker)
        if worker:
            worker.stop()
            setattr(self, attr_worker, None)
            label.clear()
            label.setText(f"Camera {cam_id} 未接続")

        # --- ボタン・ステータス初期化
        calib_btn.setEnabled(False)
        status_lbl.setText("未キャリブレーション")

        # --- 「未選択」が選ばれた場合
        if index == 0:
            self._update_combo_enabled_states()
            return

        # ===== 重複選択チェック =====
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
        # =====

        # --- 新しいカメラインデックスでプレビュー開始
        device_id: int = index - 1
        worker = CameraCaptureWorker(device_id)
        worker.image_ready.connect(
            lambda qimg, lbl=label: lbl.setPixmap(
                QPixmap.fromImage(qimg).scaled(
                    480, 480, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        )
        worker.start()
        setattr(self, attr_worker, worker)

        # --- ボタンを有効化
        calib_btn.setEnabled(True)

        # --- UI 状態更新
        self._update_combo_enabled_states()
        self._refresh_calib_ui(cam_id)

    # ===== キャリブレーション開始ハンドラ =====
    def _on_calibration_start(self, cam_id: int) -> None:
        """
        キャリブレーション開始ボタン押下時の処理。
        """
        # --- 対象 UI／属性
        combo = self.camera1_combo if cam_id == 1 else self.camera2_combo
        calib_btn = self.calib1_btn if cam_id == 1 else self.calib2_btn
        status_lbl = self.calib1_status if cam_id == 1 else self.calib2_status
        attr_worker = "calib1_worker" if cam_id == 1 else "calib2_worker"

        # --- 未選択防止（二重確認）
        if combo.currentIndex() == 0:
            return

        # --- 既に動作中なら無視
        if getattr(self, attr_worker):
            return

        # --- UI 更新
        calib_btn.setEnabled(False)
        status_lbl.setText("キャリブレーション中...")

        # --- ワーカ起動
        device_id: int = combo.currentIndex() - 1
        calib_worker = CameraCalibrator(device_id)
        calib_worker.progress.connect(
            lambda p, lbl=status_lbl: lbl.setText(f"キャリブレーション中... ({p}%)")
        )
        calib_worker.finished.connect(
            lambda res, lbl=status_lbl, btn=calib_btn, attr=attr_worker:
                self._on_calibration_finished(lbl, btn, attr, res)
        )
        calib_worker.failed.connect(
            lambda msg, lbl=status_lbl, btn=calib_btn, attr=attr_worker:
                self._on_calibration_failed(lbl, btn, attr, msg)
        )
        calib_worker.start()
        setattr(self, attr_worker, calib_worker)

    # ===== キャリブレーション完了コールバック =====
    def _on_calibration_finished(
        self,
        status_lbl: QLabel,
        calib_btn: QPushButton,
        attr_worker: str,
        result: object
    ) -> None:
        """
        成功時にステータスを更新し、ワーカを破棄する。
        """
        status_lbl.setText("キャリブレーション完了")
        calib_btn.setEnabled(True)
        setattr(self, attr_worker, None)
        self._refresh_calib_ui(1 if attr_worker == "calib1_worker" else 2)

    # ===== キャリブレーション失敗コールバック =====
    def _on_calibration_failed(
        self,
        status_lbl: QLabel,
        calib_btn: QPushButton,
        attr_worker: str,
        message: str
    ) -> None:
        """
        失敗時にユーザ通知し、ステータスを更新する。
        """
        QMessageBox.critical(self, "キャリブレーション失敗", message)
        status_lbl.setText("未キャリブレーション")
        calib_btn.setEnabled(True)
        setattr(self, attr_worker, None)
        self._refresh_calib_ui(1 if attr_worker == "calib1_worker" else 2)

    # ===== コンボアイテムの Enabled 状態を更新 =====
    def _update_combo_enabled_states(self) -> None:
        """
        片方で選択済みのカメラは、もう一方のコンボでは選択不可 (disabled) にする。
        """
        selected1: int = self.camera1_combo.currentIndex()
        selected2: int = self.camera2_combo.currentIndex()

        for idx in range(self.camera1_combo.count()):
            item1 = self.camera1_combo.model().item(idx)
            item2 = self.camera2_combo.model().item(idx)

            item1.setEnabled(idx == 0 or idx != selected2)
            item2.setEnabled(idx == 0 or idx != selected1)
    
    # ===== キャリブレーション UI 更新 =====
    def _refresh_calib_ui(self, cam_id: int) -> None:
        """
        コンボの選択状態とワーカの有無を見てキャリブレーションボタンの Enabled を更新する。
        """
        combo      = self.camera1_combo if cam_id == 1 else self.camera2_combo
        calib_btn  = self.calib1_btn    if cam_id == 1 else self.calib2_btn
        worker     = self.calib1_worker if cam_id == 1 else self.calib2_worker

        # --- 未選択 or ワーカ動作中なら無効
        calib_btn.setEnabled(combo.currentIndex() != 0 and worker is None)

    # ===== closeEvent オーバーライド =====
    def closeEvent(self, event) -> None:  # type: ignore[override]
        """
        ウィンドウが閉じられるときにキャプチャ／キャリブレーションスレッドを停止する。
        """
        # --- プレビュー停止
        for worker in (self.cam1_worker, self.cam2_worker):
            if worker:
                worker.stop()

        # --- キャリブレータ停止
        for worker in (self.calib1_worker, self.calib2_worker):
            if worker:
                worker.stop()

        super().closeEvent(event)
