# ===== 標準ライブラリのインポート =====
from typing import Tuple, List
# =====

# ===== PySide6 ウィジェット関連のインポート =====
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLayout, QVBoxLayout,
    QHBoxLayout, QGroupBox, QComboBox, QScrollArea
)
# =====

# ===== PySide6 コアモジュールのインポート =====
from PySide6.QtCore import Qt
# =====

# ===== 自作モジュールのインポート（相対パス） =====
# --- GUIのスタイル定義（色定数）
from .style_constants import BACKGROUND_COLOR, FOREGROUND_COLOR
# --- カメラ接続監視用マネージャ
from ..camera.camera_manager import QtCameraManager
# =====

class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウを表すクラス
    """

    def __init__(self) -> None:
        """
        メインウィンドウを初期化し、UIを構築する。
        """
        super().__init__()

        # ===== ウィンドウタイトル設定 =====
        # --- アプリ名をタイトルバーに表示
        self.setWindowTitle("ESTiVision")
        # =====

        # ===== UI構築 =====
        # --- レイアウトやウィジェットを初期化
        self._setup_ui()
        # =====

        # ===== カメラ監視マネージャの初期化とシグナル接続 =====
        # --- 接続／切断の変化を受け取ってコンボを更新する
        self.qt_cam_mgr: QtCameraManager = QtCameraManager()
        self.qt_cam_mgr.cameras_changed.connect(self._on_cameras_changed)
        # =====

        # ===== ウィンドウ幅を中身にフィットさせ固定 =====
        # --- サイズ計算後、横幅のみ固定
        self.adjustSize()
        self.setFixedWidth(self.width())
        # =====

    # ===== UI初期化処理 =====
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

        # ===== コンテンツ幅の調整 =====
        content_width: int = cameras_section.sizeHint().width()
        content_widget.setFixedWidth(content_width + 8)  # 枠線余白分を追加
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
        scroll_bar_width = scroll_area.verticalScrollBar().sizeHint().width()
        frame_padding = scroll_area.frameWidth() * 2
        total_width = content_width + scroll_bar_width + frame_padding + 8
        self.adjustSize()
        self.setFixedWidth(total_width)
        # =====

    # ===== カメラセクションの作成 =====
    def _create_cameras_section(self) -> QGroupBox:
        """
        複数カメラのプレビュー用グループを横並びにまとめたセクションを返す。
        """
        camera1_group, self.camera1_combo, self.camera1_label = self._create_camera_group(1)
        camera2_group, self.camera2_combo, self.camera2_label = self._create_camera_group(2)

        layout: QHBoxLayout = QHBoxLayout()
        layout.addWidget(camera1_group)
        layout.addWidget(camera2_group)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.setSpacing(16)
        layout.setContentsMargins(16, 8, 16, 16)

        group: QGroupBox = QGroupBox("Camera preview")
        group.setLayout(layout)
        return group

    # ===== 個別カメラグループの作成 =====
    def _create_camera_group(self, camera_id: int) -> Tuple[QGroupBox, QComboBox, QLabel]:
        """
        指定IDのカメラ用コンボボックスと映像表示ラベルを含むグループを生成する。
        """
        combo: QComboBox = QComboBox()
        combo.addItem("未選択")
        combo.setFixedWidth(480)

        label: QLabel = QLabel(f"Camera {camera_id} 映像")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(480, 480)
        label.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {FOREGROUND_COLOR};
            border-radius: 8px;
        """)

        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(combo)
        layout.addWidget(label)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.setContentsMargins(16, 8, 16, 16)

        group: QGroupBox = QGroupBox(f"Camera {camera_id}")
        group.setLayout(layout)
        return group, combo, label

    # ===== カメラ一覧更新ハンドラ =====
    def _on_cameras_changed(self, device_names: List[str]) -> None:
        """
        カメラ接続状態の変化時にコンボボックスを更新する。
        """
        # --- それぞれのコンボを一時的に無効化して更新
        for combo in (self.camera1_combo, self.camera2_combo):
            combo.blockSignals(True)      # --- シグナル抑制
            combo.clear()                 # --- 既存アイテムクリア
            combo.addItem("未選択")
            for name in device_names:     # --- 新しいデバイス名を追加
                combo.addItem(name)
            combo.blockSignals(False)     # --- シグナル再有効化
        # =====
