from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QGroupBox, QComboBox
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

        # --- ウィンドウタイトルとサイズを設定
        self.setWindowTitle("ESTiVision フルトラ GUI")
        # self.setMinimumSize(1280, 720)

        # --- UI初期化
        self._setup_ui()

    # ===== UI初期化処理

    def _setup_ui(self):
        """
        UIレイアウトを設定する
        """
        # --- 中央ウィジェットとレイアウトを作成
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # --- カメラセクションを作成して追加
        cameras_section = self._create_cameras_section()
        main_layout.addWidget(cameras_section)

        # --- レイアウトを中央ウィジェットに設定
        central_widget.setLayout(main_layout)

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
