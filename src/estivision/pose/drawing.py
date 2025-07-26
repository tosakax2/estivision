"""Pose drawing utilities."""

# ===== インポート =====
import cv2 as cv
import numpy as np
# ====


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
    (255, 0, 85),
    (255, 0, 0),
    (255, 85, 0),
    (255, 170, 0),
    (255, 255, 0),
    (170, 255, 0),
    (85, 255, 0),
    (0, 255, 0),
    (0, 255, 85),
    (0, 255, 170),
    (0, 255, 255),
    (0, 170, 255),
    (0, 85, 255),
    (0, 0, 255),
    (85, 0, 255),
    (170, 0, 255),
    (255, 0, 255),
]


def draw_pose(img: np.ndarray, kps: np.ndarray, scores: np.ndarray, thr: float = 0.2) -> np.ndarray:
    """Return an image with pose skeleton drawn."""
    disp = img.copy()
    for i, (p1, p2) in enumerate(_SKELETON):
        if scores[p1] > thr and scores[p2] > thr:
            color = _SKELETON_COLORS[i % len(_SKELETON_COLORS)]
            cv.line(disp, tuple(kps[p1]), tuple(kps[p2]), color, 2)
    for (x, y), s in zip(kps, scores):
        if s > thr:
            cv.circle(disp, (int(x), int(y)), 5, (0, 0, 0), -1)
            cv.circle(disp, (int(x), int(y)), 3, (255, 255, 255), -1)
    return disp

__all__ = ["draw_pose"]
