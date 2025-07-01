# ===== 標準ライブラリのインポート =====
# --- 型ヒント用
from typing import Tuple
# ==========

# ===== PySide6 ウィジェット関連のインポート =====
# --- メインウィンドウ、レイアウト、ウィジェット用
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLayout, QVBoxLayout,
    QHBoxLayout, QGroupBox, QComboBox, QScrollArea
)
# ==========

# ===== PySide6 コアモジュールのインポート =====
# --- Qt の定数やフラグ用
from PySide6.QtCore import Qt
# ==========

# ===== 自作モジュールのインポート（相対パス） =====
# --- GUIのスタイル定義（色定数）を取得
from .style_constants import BACKGROUND_COLOR, FOREGROUND_COLOR
# ==========

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
        # --- アプリケーション名をタイトルバーに表示
        self.setWindowTitle("ESTiVision")
        # ==========

        # ===== UI構築 =====
        # --- レイアウトやウィジェットを初期化
        self._setup_ui()
        # ==========

        # ===== ウィンドウ幅を中身にフィットさせ固定 =====
        # --- サイズを計算してから横幅のみ固定
        self.adjustSize()
        self.setFixedWidth(self.width())
        # ==========

    # ===== UI初期化処理 =====
    def _setup_ui(self) -> None:
        """
        中央ウィジェットにスクロール対応のコンテンツをセットアップする。
        """
        # ===== コンテンツウィジェットとレイアウトの生成 =====
        # --- スクロール領域内に配置するコンテンツ用ウィジェット
        content_widget: QWidget = QWidget()
        # --- 垂直方向にウィジェットを積み上げるレイアウト
        content_layout: QVBoxLayout = QVBoxLayout(content_widget)
        # --- 上寄せにして余白を下に伸ばす
        content_layout.setAlignment(Qt.AlignTop)
        # ==========

        # ===== カメラ選択セクションの追加 =====
        # --- QGroupBoxでまとめたカメラセクションを生成
        cameras_section: QGroupBox = self._create_cameras_section()
        content_layout.addWidget(cameras_section)
        # ==========

        # ===== コンテンツ幅の調整 =====
        # --- セクションの推奨幅を取得して固定
        content_width: int = cameras_section.sizeHint().width()
        content_widget.setFixedWidth(content_width)
        # --- 枠線が切れないよう少し余白を追加
        margin_compensation: int = 8
        content_widget.setFixedWidth(content_width + margin_compensation)
        # ==========

        # ===== スクロールエリアの生成と設定 =====
        scroll_area: QScrollArea = QScrollArea()
        scroll_area.setWidgetResizable(True)
        # --- コンテンツウィジェットをセット
        scroll_area.setWidget(content_widget)
        # --- 横スクロール禁止、縦スクロールは必要に応じて表示
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # --- メインウィンドウの中央ウィジェットとして設定
        self.setCentralWidget(scroll_area)
        # ==========

        # ===== ウィンドウ幅の最終調整 =====
        # --- コンテンツ＋スクロールバー＋フレーム幅＋余白を考慮して固定
        self.adjustSize()
        scroll_bar_width: int = scroll_area.verticalScrollBar().sizeHint().width()
        frame_padding: int = scroll_area.frameWidth() * 2  # フレーム幅分のパディング取得
        total_width: int = content_width + scroll_bar_width + frame_padding + margin_compensation
        self.setFixedWidth(total_width)
        # ==========

    # ===== カメラセクションの作成 =====
    def _create_cameras_section(self) -> QGroupBox:
        """
        複数カメラのプレビュー用グループを横並びにまとめたセクションを返す。
        """
        # ===== 各カメラグループの生成 =====
        camera1_group, self.camera1_combo, self.camera1_label = self._create_camera_group(1)
        camera2_group, self.camera2_combo, self.camera2_label = self._create_camera_group(2)
        # ==========

        # ===== レイアウト設定 =====
        layout: QHBoxLayout = QHBoxLayout()
        # --- 各カメラグループを横方向に追加
        layout.addWidget(camera1_group)
        layout.addWidget(camera2_group)
        # --- 内包するウィジェットのサイズにレイアウトを固定
        layout.setSizeConstraint(QLayout.SetFixedSize)
        # --- グループ間のスペースを設定
        layout.setSpacing(16)
        # --- セクション全体のパディング（left, top, right, bottom）
        layout.setContentsMargins(16, 8, 16, 16)
        # ==========

        # ===== セクション用グループボックスの生成 =====
        group: QGroupBox = QGroupBox("Camera preview")
        group.setLayout(layout)
        # ==========

        return group

    # ===== 個別カメラグループの作成 =====
    def _create_camera_group(self, camera_id: int) -> Tuple[QGroupBox, QComboBox, QLabel]:
        """
        指定IDのカメラ用コンボボックスと映像表示ラベルを含むグループを生成する。
        """
        # ===== コンボボックスの生成 =====
        combo: QComboBox = QComboBox()
        # --- 未選択状態の初期アイテムを追加
        combo.addItem("未選択")
        # --- ラベルと同幅に固定
        combo.setFixedWidth(480)
        # ==========

        # ===== ラベルの生成 =====
        label: QLabel = QLabel(f"Camera {camera_id} 映像")
        # --- テキストを中央寄せ
        label.setAlignment(Qt.AlignCenter)
        # --- 正方形サイズに固定
        label.setFixedSize(480, 480)
        # --- 背景色・文字色・角丸をスタイルシートで設定
        label.setStyleSheet(f"""
            background-color: {BACKGROUND_COLOR};
            color: {FOREGROUND_COLOR};
            border-radius: 8px;
        """)
        # ==========

        # ===== レイアウト生成 =====
        layout: QVBoxLayout = QVBoxLayout()
        # --- コンボボックスとラベルを縦に追加
        layout.addWidget(combo)
        layout.addWidget(label)
        # --- 内包するウィジェットのサイズにレイアウトを固定
        layout.setSizeConstraint(QLayout.SetFixedSize)
        # --- 内側パディング（left, top, right, bottom）を設定
        layout.setContentsMargins(16, 8, 16, 16)
        # ==========

        # ===== グループボックス生成 =====
        group: QGroupBox = QGroupBox(f"Camera {camera_id}")
        group.setLayout(layout)
        # ==========

        return group, combo, label
