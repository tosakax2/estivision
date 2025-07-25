# ===== インポート =====
# --- 標準ライブラリ ---
from pathlib import Path
from typing import Tuple

# --- 外部ライブラリ ---
import cv2
import numpy as np
import onnxruntime as ort
# ====


# ===== 定数定義 =====
# --- MoveNet Lightning (single-pose) ONNX モデルパス ---
DEFAULT_MODEL_PATH: Path = Path("models/movenet_singlepose_lightning_v4.onnx")
# --- 入力解像度（Lightning は 192×192） ---
INPUT_SIZE: Tuple[int, int] = (192, 192)
# --- 出力キーポイント数 ---
NUM_KEYPOINTS: int = 17
# ====


class PoseEstimator:
    """ONNX Runtime で MoveNet Lightning を実行する簡易推定器。"""

    # ===== コンストラクタ =====
    def __init__(self, model_path: Path | str = DEFAULT_MODEL_PATH) -> None:
        """model_path の ONNX を読み込みセッションを初期化する。"""
        self._model_path: Path = Path(model_path)
        if not self._model_path.exists():
            raise FileNotFoundError(
                f"モデルが見つかりません：{self._model_path}"
            )

        # --- ONNX Runtime セッション生成 (CPU) ---
        self._session: ort.InferenceSession = ort.InferenceSession(
            str(self._model_path),
            providers=["CPUExecutionProvider"],
        )
        self._input_name: str = self._session.get_inputs()[0].name

    # ===== パブリック API =====
    def estimate(self, bgr: np.ndarray) -> np.ndarray:
        """BGR画像から (17,3)[x,y,score] のキーポイントを返す。"""
        inp: np.ndarray = self._preprocess(bgr)
        outputs: list[np.ndarray] = self._session.run(None, {self._input_name: inp})
        # --- MoveNet の出力は (1,1,17,3) → squeeze で (17,3) ---
        keypoints: np.ndarray = outputs[0].squeeze().astype(np.float32)
        # --- 入力解像度基準の x,y を元画像座標にスケーリング ---
        h, w = bgr.shape[:2]
        keypoints[:, 0] *= w  / INPUT_SIZE[0]   # x
        keypoints[:, 1] *= h  / INPUT_SIZE[1]   # y
        return keypoints  # shape=(17,3)

    # ===== 内部ヘルパ =====
    def _preprocess(self, bgr: np.ndarray) -> np.ndarray:
        """BGR→RGB, リサイズ, int32型 (1,192,192,3) に変換。"""
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, INPUT_SIZE, interpolation=cv2.INTER_LINEAR)
        tensor = resized.astype(np.int32)  # int32型へ
        tensor = tensor[None, ...]  # (1,H,W,3)
        return tensor
