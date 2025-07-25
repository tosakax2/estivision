# ===== インポート =====
# --- 標準ライブラリ ---
import sys
from pathlib import Path

# --- 外部ライブラリ ---
import cv2
import numpy as np

# --- パス設定 ---
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# --- 自作モジュール ---
from estivision.pose.pose_estimator import PoseEstimator
# ====


# ===== 定数定義 =====
# --- キーポイント名称（MoveNet公式順） ---
KEYPOINT_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]

# --- 骨格エッジ定義 ---
SKELETON_EDGES = [
    (0, 1), (0, 2), (1, 3), (2, 4),
    (0, 5), (0, 6), (5, 7), (7, 9),
    (6, 8), (8,10), (5, 6), (5,11),
    (6,12), (11,12), (11,13), (13,15),
    (12,14), (14,16),
]
# ====


def test_pose_estimation() -> None:
    """静止画像で PoseEstimator が (17,3) 配列を返し、各関節を出力・可視化する。"""
    # --- サンプル画像パス ---
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
    scores = kps[:, 2]
    assert np.all((0.0 <= scores) & (scores <= 1.0)), "信頼度スコアが 0-1 範囲外"

    # --- 各関節の座標とスコアを出力 ---
    print("===== 推定キーポイント =====")
    for idx, (name, (x, y, score)) in enumerate(zip(KEYPOINT_NAMES, kps)):
        print(f"{idx:2}: {name:15s} x={x:.2f}, y={y:.2f}, score={score:.3f}")
    print("====")

    # --- デバッグ出力で値域確認 ---
    x_vals = kps[:, 0]
    y_vals = kps[:, 1]
    print(f"x min={x_vals.min():.2f}, max={x_vals.max():.2f}")
    print(f"y min={y_vals.min():.2f}, max={y_vals.max():.2f}")
    print(f"image shape: h={bgr.shape[0]}, w={bgr.shape[1]}")

    # --- キーポイント可視化の前に骨格線を描画 ---
    h, w = bgr.shape[:2]
    x_max = kps[:, 0].max()
    y_max = kps[:, 1].max()

    for idx_from, idx_to in SKELETON_EDGES:
        x1, y1, s1 = kps[idx_from]
        x2, y2, s2 = kps[idx_to]
        # スコアが高い点のみ線分描画
        if s1 > 0.3 and s2 > 0.3:
            cx1 = int(x1 / x_max * w)
            cy1 = int(y1 / y_max * h)
            cx2 = int(x2 / x_max * w)
            cy2 = int(y2 / y_max * h)
            cv2.line(bgr, (cx1, cy1), (cx2, cy2), (255, 128, 0), 2)

    # --- その後にキーポイント（円＋ラベル）描画 ---
    for idx, (x, y, score) in enumerate(kps):
        if score > 0.3:
            cx = int(x / x_max * w)
            cy = int(y / y_max * h)
            cv2.circle(bgr, (cx, cy), 5, (0, 255, 0), -1)
            cv2.putText(
                bgr,
                KEYPOINT_NAMES[idx],
                (cx + 6, cy - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 0), 4, cv2.LINE_AA  # 黒で太め（縁）
            )
            cv2.putText(
                bgr,
                KEYPOINT_NAMES[idx],
                (cx + 6, cy - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 1, cv2.LINE_AA  # 白で細め（文字本体）
            )

    # --- 画像表示 ---
    cv2.imshow("Pose Estimation Result", bgr)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ===== エントリポイント =====
if __name__ == "__main__":
    test_pose_estimation()
