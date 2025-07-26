# ===== インポート =====
# --- 標準ライブラリ ---
from pathlib import Path

# --- 外部ライブラリ ---
import cv2 as cv
import numpy as np
import pytest

# --- 自作モジュール ---
from estivision.pose.pose_estimator import PoseEstimator
# ====


# ===== 定数定義 =====
# --- 骨格接続ペア (MoveNet Keypoint Index) ---
_SKELETON: list[tuple[int, int]] = [
    (0, 1), (0, 2), (1, 3), (2, 4),
    (0, 5), (0, 6), (5, 7), (7, 9),
    (6, 8), (8, 10), (5, 6), (5, 11),
    (6, 12), (11, 12), (11, 13),
    (13, 15), (12, 14), (14, 16),
]
# --- 骨格ごとに色を設定 ---
_SKELETON_COLORS: list[tuple[int, int, int]] = [
    (255, 0, 85),     # 鼻～首（ピンク系）
    (255, 0, 0),      # 右目～鼻
    (255, 85, 0),     # 左目～鼻
    (255, 170, 0),    # 右耳～右目
    (255, 255, 0),    # 左耳～左目
    (170, 255, 0),    # 首～右肩
    (85, 255, 0),     # 首～左肩
    (0, 255, 0),      # 右肩～右肘
    (0, 255, 85),     # 左肩～左肘
    (0, 255, 170),    # 右肘～右手首
    (0, 255, 255),    # 左肘～左手首
    (0, 170, 255),    # 首～右腰
    (0, 85, 255),     # 首～左腰
    (0, 0, 255),      # 右腰～右膝
    (85, 0, 255),     # 左腰～左膝
    (170, 0, 255),    # 右膝～右足首
    (255, 0, 255),    # 左膝～左足首
]
# ====


def _draw_pose(img: np.ndarray, kps: np.ndarray, scores: np.ndarray, thr: float = 0.2) -> np.ndarray:
    """骨格・キーポイントを描画。"""
    disp = img.copy()
    for i, (p1, p2) in enumerate(_SKELETON):
        if scores[p1] > thr and scores[p2] > thr:
            color = _SKELETON_COLORS[i % len(_SKELETON_COLORS)]
            cv.line(disp, tuple(kps[p1]), tuple(kps[p2]), color, 2)
    for (x, y), s in zip(kps, scores):
        if s > thr:
            cv.circle(disp, (int(x), int(y)), 5, (0, 0, 0), -1)      # 黒縁
            cv.circle(disp, (int(x), int(y)), 3, (255, 255, 255), -1)  # 白丸
    return disp

# --- テスト用フィクスチャ ---
@pytest.fixture(scope="module")
def estimator() -> PoseEstimator:
    """PoseEstimator インスタンスを返す。"""
    model_path = (
        Path(__file__).resolve().parents[1]
        / "data"
        / "models"
        / "movenet_singlepose_lightning_v4.onnx"
    )
    if not model_path.is_file():
        pytest.skip("MoveNet ONNX モデルが見つからないためテストをスキップします。")
    return PoseEstimator(model_type="lightning", model_dir=model_path.parent, providers=["CPUExecutionProvider"])

# --- 推論がエラーにならず形状が正しいか確認 ---
def test_estimate_output_shape(estimator: PoseEstimator) -> None:
    """出力形状 (17,2) / (17,) であることを確認。"""
    dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
    keypoints, scores = estimator.estimate(dummy_img)

    assert keypoints.shape == (17, 2)
    assert scores.shape == (17,)
    assert np.all((0 <= scores) & (scores <= 1)), "スコアは 0.0～1.0 の範囲"

# --- 既知画像で推論し、スコアが全て 0 ではないことを確認（疎なテスト） ---
def test_estimate_non_zero(estimator: PoseEstimator) -> None:
    """推論結果が全ゼロではないことを簡易確認。"""
    # tests/assets/example.jpg があれば読み込む。無ければ黒画像でテスト。
    asset_jpg = Path(__file__).with_name("assets").joinpath("example.jpg")
    img = cv.imread(asset_jpg.as_posix()) if asset_jpg.is_file() else np.zeros((480, 640, 3), np.uint8)

    _, scores = estimator.estimate(img)

    # 少なくとも 1 点は信頼度が 0 を超える（黒画像なら 0 でも OK）
    assert np.any(scores > 0) or np.allclose(img, 0)

# --- 推論結果を描画してファイル出力 ---
def test_draw_and_save(estimator: PoseEstimator) -> None:
    """推論した骨格画像を tests/assets に保存。"""
    asset_dir = Path(__file__).with_name("assets")
    asset_jpg = asset_dir.joinpath("example.jpg")
    img = cv.imread(asset_jpg.as_posix()) if asset_jpg.is_file() else np.zeros((480, 640, 3), np.uint8)

    kps, scores = estimator.estimate(img)
    drawn = _draw_pose(img, kps, scores)
    out_path = asset_dir.joinpath("pose_result.png")
    cv.imwrite(out_path.as_posix(), drawn)
    assert out_path.is_file()


if __name__ == "__main__":
    print("テストファイルが実行されました")
