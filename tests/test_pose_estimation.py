# ===== インポート =====
# --- 標準ライブラリ ---
import sys
from pathlib import Path

# --- 外部ライブラリ ---
import cv2
import numpy as np
import pytest

# --- パス設定 ---
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# --- 自作モジュール ---
from estivision.pose.pose_estimator import PoseEstimator
# ====


# ===== テスト =====
def test_pose_estimation() -> None:
    """静止画像で PoseEstimator が (17,3) 配列を返すことを検証する。"""
    # --- サンプル画像パス（リポジトリ外なら引数に応じて修正） ---
    sample_img_path: Path = Path("tests/assets/sample_pose.png")
    assert sample_img_path.exists(), f"テスト画像がありません: {sample_img_path}"

    # --- 画像読み込み ---
    bgr = cv2.imread(str(sample_img_path))
    assert bgr is not None, "cv2.imread 失敗"

    # --- 推定 ---
    estimator = PoseEstimator()
    kps: np.ndarray = estimator.estimate(bgr)

    # --- 形状／値域チェック ---
    assert kps.shape == (17, 3), "出力 shape が (17,3) ではない"
    # スコア 0-1 範囲チェック
    scores = kps[:, 2]
    assert np.all((0.0 <= scores) & (scores <= 1.0)), "信頼度スコアが 0-1 範囲外"

    # --- 可視出力（任意） ---
    # cv2.circle 等で描画し可視確認する場合は適宜追加


# ===== エントリポイント =====
if __name__ == "__main__":
    sys.exit(pytest.main([__file__]))
