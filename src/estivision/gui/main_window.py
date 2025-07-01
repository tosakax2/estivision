from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLayout, QVBoxLayout,
    QHBoxLayout, QGroupBox, QComboBox, QScrollArea
)
from PySide6.QtCore import Qt

# ===== 色定数をインポート
from .style_constants import BACKGROUND_COLOR, FOREGROUND_COLOR


class MainWindow(QMainWindow):
    """
    アプリケーションのメインウィンドウを表すクラス
    """

    def __init__(self) -> None:
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
    def _setup_ui(self) -> None:
        """
        UIレイアウトを設定する
        """
        # ===== 中身のウィジェット
        content_widget: QWidget = QWidget()
        content_layout: QVBoxLayout = QVBoxLayout(content_widget)

        # --- 上寄せにする
        content_layout.setAlignment(Qt.AlignTop)

        # --- カメラセクションの追加
        cameras_section: QGroupBox = self._create_cameras_section()
        content_layout.addWidget(cameras_section)

        # --- 中身の横幅を決定（手動で固定）
        content_width: int = cameras_section.sizeHint().width()
        content_widget.setFixedWidth(content_width)

        # --- 枠線が見切れないように余白を少し加える
        margin_compensation: int = 8
        content_widget.setFixedWidth(content_width + margin_compensation)

        # ===== スクロールエリアの作成
        scroll_area: QScrollArea = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        # --- 横スクロールは常に無効、縦スクロールは必要に応じて
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # --- スクロールエリアを中央ウィジェットに設定
        self.setCentralWidget(scroll_area)

        # ===== ウィンドウ横幅を完全にフィットさせる
        self.adjustSize()

        # --- スクロールバーとフレームの幅を考慮
        scroll_bar_width: int = scroll_area.verticalScrollBar().sizeHint().width()
        frame_padding: int = scroll_area.frameWidth() * 2

        # --- 横幅を固定（中身 + スクロールバー + フレーム + 枠補正）
        total_width: int = content_width + scroll_bar_width + frame_padding + margin_compensation
        self.setFixedWidth(total_width)


    # ===== カメラセクションの作成
    def _create_cameras_section(self) -> QGroupBox:
        """
        複数のカメラグループを横並びにして1つのセクションとして返す
        """
        # --- 各カメラグループを生成
        camera1_group, self.camera1_combo, self.camera1_label = self._create_camera_group(1)
        camera2_group, self.camera2_combo, self.camera2_label = self._create_camera_group(2)

        # --- 横並びに配置
        layout: QHBoxLayout = QHBoxLayout()
        layout.addWidget(camera1_group)
        layout.addWidget(camera2_group)

        # --- レイアウトが縦に伸びないように制約をかける
        layout.setSizeConstraint(QLayout.SetFixedSize)

        # --- グループ間のスペースを設定
        layout.setSpacing(16)

        # --- パディングを設定（left, top, right, bottom）
        layout.setContentsMargins(16, 8, 16, 16)

        # --- 全体のカメラ表示エリアとしてまとめる
        group: QGroupBox = QGroupBox("Camera preview")
        group.setLayout(layout)

        return group


    # ===== 個別カメラグループの作成
    def _create_camera_group(self, camera_id: int) -> tuple[QGroupBox, QComboBox, QLabel]:
        """
        指定したカメラIDに対応するカメラグループを作成する

        :param camera_id: カメラ番号 (1 または 2)
        :return: (グループボックス, コンボボックス, 映像表示ラベル)
        """
        # --- カメラ選択用コンボボックス
        combo: QComboBox = QComboBox()
        combo.addItem("未選択")
        combo.setFixedWidth(480)  # ← QLabel と合わせる

        # --- 映像表示用のラベル
        label: QLabel = QLabel(f"Camera {camera_id} 映像")
        label.setAlignment(Qt.AlignCenter)
        label.setFixedSize(480, 480)
        label.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {FOREGROUND_COLOR};
            border-radius: 8px;
        """)

        # --- レイアウトに部品を追加
        layout: QVBoxLayout = QVBoxLayout()
        layout.addWidget(combo)
        layout.addWidget(label)

        # --- レイアウトが縦に伸びないように制約をかける
        layout.setSizeConstraint(QLayout.SetFixedSize)

        # --- パディングを追加（left, top, right, bottom）
        layout.setContentsMargins(16, 8, 16, 16)

        # --- グループボックスで囲む
        group: QGroupBox = QGroupBox(f"Camera {camera_id}")
        group.setLayout(layout)

        return group, combo, label
