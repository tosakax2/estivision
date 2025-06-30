from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QGroupBox, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt

# === 色定数をインポート
from .style_constants import BACKGROUND_COLOR, FOREGROUND_COLOR


class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウを表すクラス
    """
    def __init__(self):
        """
        メインウィンドウの初期化を行う
        """
        super().__init__()

        # --- タイトル設定
        self.setWindowTitle("ESTiVision")

        # --- UI構築
        self._setup_ui()

        # --- 中身にフィットするサイズを計算して横幅を固定
        self.adjustSize()
        self.setFixedWidth(self.width())

    # ===== UI初期化処理

    def _setup_ui(self):
        """
        UIレイアウトを設定する
        """
        # ===== スクロール可能なメインUIの作成

        # --- 中身のウィジェット（カメラなど）
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # --- セクションを追加
        cameras_section = self._create_cameras_section()
        content_layout.addWidget(cameras_section)

        # --- スクロールエリアを作成して中身をセット
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        # --- スクロールエリアをメインに設定
        self.setCentralWidget(scroll_area)

    # ===== カメラセクションの作成

    def _create_cameras_section(self) -> QGroupBox:
        """
        複数のカメラグループを横並びにして1つのセクションとして返す
        """
        # --- 各カメラグループを生成
        camera1_group, self.camera1_combo, self.camera1_label = self._create_camera_group(1)
        camera2_group, self.camera2_combo, self.camera2_label = self._create_camera_group(2)

        # --- 横並びに配置
        layout = QHBoxLayout()
        layout.addWidget(camera1_group)
        layout.addWidget(camera2_group)

        # --- 全体のカメラ表示エリアとしてまとめる
        group = QGroupBox("カメラ映像")
        group.setLayout(layout)

        return group

    # ===== 個別カメラグループの作成

    def _create_camera_group(self, camera_id: int) -> tuple[QGroupBox, QComboBox, QLabel]:
        """
        指定したカメラIDに対応するカメラグループを作成する
        """
        # --- カメラ選択用コンボボックス
        combo = QComboBox()
        combo.addItem("未選択")

        # --- 映像表示用のラベル
        label = QLabel(f"Camera {camera_id} 映像")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(480, 480)
        label.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {FOREGROUND_COLOR};
            border-radius: 8px;
        """)

        # --- グループボックスにまとめる
        group = QGroupBox(f"Camera {camera_id}")
        layout = QVBoxLayout()
        layout.addWidget(combo)
        layout.addWidget(label)
        group.setLayout(layout)

        return group, combo, label
