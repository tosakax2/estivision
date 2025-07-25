# === 標準ライブラリのインポート ===
from pathlib import Path
from typing import List, Tuple

# === 外部ライブラリのインポート ===
import cv2 as cv
import numpy as np
import onnxruntime as ort

# === 定数定義 ===
_KEYPOINT_NAMES: Tuple[str, ...] = (
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
)

_MODEL_INFO = {
    "lightning": {"file": "movenet_singlepose_lightning_v4.onnx", "input_size": 192},
    "thunder":   {"file": "movenet_singlepose_thunder_v4.onnx",   "input_size": 256},
}


class PoseEstimator:
    """MoveNet で単一人物姿勢推定を行うラッパークラス。"""

    # - サポートされるモデルタイプ -
    SUPPORTED_MODELS: Tuple[str, ...] = tuple(_MODEL_INFO.keys())

    # --------------------------------------------------------------------- #
    def __init__(
        self,
        model_type: str = "lightning",
        *,
        model_dir: Path | None = None,
        providers: List[str] | None = None,
    ) -> None:
        """モデルを読み込み、推論セッションを初期化。"""
        if model_type not in self.SUPPORTED_MODELS:
            raise ValueError(f"model_type must be one of {self.SUPPORTED_MODELS}")

        # - モデルパス決定 -
        model_dir = model_dir or (Path(__file__).resolve().parents[2] / "data" / "models")
        model_path: Path = model_dir / _MODEL_INFO[model_type]["file"]
        if not model_path.is_file():
            raise FileNotFoundError(f"モデルファイルが見つかりません: {model_path}")

        # - ONNX Runtime プロバイダ設定 -
        if providers is None:
            # Radeon 環境など GPU が使えない場合を考慮し CPU を最後にフォールバック
            providers = [
                "CUDAExecutionProvider",      # NVIDIA GPU
                "DirectMLExecutionProvider",  # AMD / Intel GPU
                "CPUExecutionProvider",
            ]

        self._input_size: int = _MODEL_INFO[model_type]["input_size"]
        self._session: ort.InferenceSession = ort.InferenceSession(
            model_path.as_posix(),
            providers=providers,
        )
        self._input_name: str = self._session.get_inputs()[0].name
        self._output_name: str = self._session.get_outputs()[0].name

    # --------------------------------------------------------------------- #
    def estimate(self, image_bgr: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """1 枚の BGR 画像から 17 点の (x, y) と score を返す。"""
        orig_h, orig_w = image_bgr.shape[:2]

        # - 前処理 -
        input_tensor = cv.resize(image_bgr, (self._input_size, self._input_size))
        input_tensor = cv.cvtColor(input_tensor, cv.COLOR_BGR2RGB)
        input_tensor = input_tensor.astype(np.int32)[None, ...]  # shape: (1,H,W,3)

        # - 推論 -
        outputs = self._session.run(
            [self._output_name],
            {self._input_name: input_tensor},
        )[0]  # shape: (1,1,17,3)
        kps_scores = np.squeeze(outputs)  # shape: (17,3)

        # - 後処理：元解像度へ座標スケールバック -
        keypoints_px = np.stack(
            [
                (kps_scores[:, 1] * orig_w).astype(np.int32),
                (kps_scores[:, 0] * orig_h).astype(np.int32),
            ],
            axis=1,
        )  # shape: (17,2)

        scores = kps_scores[:, 2]

        return keypoints_px, scores

    # --------------------------------------------------------------------- #
    @property
    def keypoint_names(self) -> Tuple[str, ...]:
        """キーポイント名のタプルを返す。"""
        return _KEYPOINT_NAMES
