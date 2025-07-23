# ===== PySide6 インポート =====
from PySide6.QtWidgets import QComboBox
# =====


class SafeComboBox(QComboBox):
    """
    ドロップダウンが開いていないときはホイールイベントを無視する ComboBox。
    """
    def wheelEvent(self, event) -> None:  # type: ignore[override]
        """
        ドロップダウン表示時のみ既定動作。未表示なら無視してフリーズを防止。
        """
        if self.view().isVisible():           # ▼ が開いている？
            super().wheelEvent(event)         # → 通常のホイール動作
        else:
            event.ignore()                    # → 何もしない
