from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt

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
        self.setWindowTitle("ESTiVision")

        # --- メインUIの構築
        self._setup_ui()


    def _setup_ui(self):
        """
        UIレイアウトを設定する
        """
        # ===== 中央ウィジェットとメインレイアウトの作成
        # --- ウィンドウ全体の土台を作る
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # ===== カメラ映像用の QLabel を作成
        # --- Camera 1 ラベル
        self.camera1_label = QLabel("Camera 1 映像")
        self.camera1_label.setAlignment(Qt.AlignCenter)
        self.camera1_label.setFixedSize(480, 480)
        self.camera1_label.setStyleSheet("""
            background-color: black;
            border-radius: 8px;
        """)

        # --- Camera 2 ラベル
        self.camera2_label = QLabel("Camera 2 映像")
        self.camera2_label.setAlignment(Qt.AlignCenter)
        self.camera2_label.setFixedSize(480, 480)
        self.camera2_label.setStyleSheet("""
            background-color: black;
            border-radius: 8px;
        """)

        # ===== 各カメララベルをグループボックスに入れる
        # --- Camera 1 グループ
        camera1_group = QGroupBox("Camera 1")
        camera1_layout = QVBoxLayout()
        camera1_layout.addWidget(self.camera1_label)
        camera1_group.setLayout(camera1_layout)

        # --- Camera 2 グループ
        camera2_group = QGroupBox("Camera 2")
        camera2_layout = QVBoxLayout()
        camera2_layout.addWidget(self.camera2_label)
        camera2_group.setLayout(camera2_layout)

        # ===== Camera 1 と Camera 2 を横に並べるレイアウトを作成
        cameras_layout = QHBoxLayout()
        cameras_layout.addWidget(camera1_group)
        cameras_layout.addWidget(camera2_group)

        # ===== 全体のカメラ表示部分をグループ化
        # --- タイトル付きの QGroupBox で見た目も整理
        cameras_group = QGroupBox("カメラ映像")
        cameras_group.setLayout(cameras_layout)

        # ===== メインレイアウトにカメラグループを追加してウィジェットに設定
        main_layout.addWidget(cameras_group)
        central_widget.setLayout(main_layout)
