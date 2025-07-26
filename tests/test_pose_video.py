# ===== 標準ライブラリのインポート =====
from pathlib import Path

# ===== 外部ライブラリのインポート =====
import cv2 as cv
import numpy as np

# ===== 自作モジュールのインポート =====
from estivision.pose.pose_estimator import PoseEstimator
from estivision.pose.drawing import draw_pose

# ===== 設定 =====
VIDEO_PATH = "tests/assets/example.mp4"       # 入力動画ファイル
OUT_PATH = "tests/assets/pose_result.mp4"     # 出力動画ファイル
MODEL_PATH = Path("data/models/movenet_singlepose_lightning_v4.onnx")

def process_video(
    video_path: str,
    out_path: str,
    estimator: PoseEstimator,
    draw_fn,
    thr: float = 0.2
) -> None:
    """
    動画全フレームに骨格プレビューを描画し、保存する。
    """
    cap = cv.VideoCapture(video_path)
    if not cap.isOpened():
        print("動画ファイルを開けません:", video_path)
        return

    # 動画情報取得
    w = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv.CAP_PROP_FPS)
    fourcc = cv.VideoWriter_fourcc(*"mp4v")
    out = cv.VideoWriter(out_path, fourcc, fps, (w, h))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 骨格推論
        kps, scores = estimator.estimate(frame)
        # 骨格描画
        drawn = draw_fn(frame, kps, scores, thr)
        out.write(drawn)

    cap.release()
    out.release()
    print("保存しました:", out_path)

if __name__ == "__main__":
    # モデル存在チェック
    if not MODEL_PATH.is_file():
        print("モデルが見つかりません:", MODEL_PATH)
        exit(1)

    # PoseEstimatorインスタンス
    estimator = PoseEstimator(
        model_type="lightning",
        model_dir=MODEL_PATH.parent,
        providers=["CPUExecutionProvider"]
    )
    # 動画処理
    process_video(VIDEO_PATH, OUT_PATH, estimator, draw_pose)
