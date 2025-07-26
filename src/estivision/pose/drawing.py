# ===== インポート =====
from __future__ import annotations
from typing import List, Tuple

import cv2                 as cv
import numpy               as np
# ====

# --- 骨格接続ペア（MoveNet 番号対応） ---
_SKELETON: list[tuple[int, int]] = [
    (0, 1), (0, 2), (1, 3), (2, 4),
    (0, 5), (0, 6), (5, 7), (7, 9),
    (6, 8), (8, 10), (5, 6), (5, 11),
    (6, 12), (11, 12), (11, 13),
    (13, 15), (12, 14), (14, 16),
]
_SKELETON_COLORS: list[tuple[int, int, int]] = [
    (255, 0, 85), (255, 0, 0), (255, 85, 0), (255, 170, 0),
    (255, 255, 0), (170, 255, 0), (85, 255, 0), (0, 255, 0),
    (0, 255, 85), (0, 255, 170), (0, 255, 255), (0, 170, 255),
    (0, 85, 255), (0, 0, 255), (85, 0, 255),
    (170, 0, 255), (255, 0, 255), (255, 0, 170)
]

def draw_pose(
    img_bgr: np.ndarray,
    kps_px: np.ndarray,
    scores: np.ndarray,
    thr: float = 0.2
) -> np.ndarray:
    """推論結果を BGR 画像に描画して返す。"""
    disp = img_bgr.copy()
    for i, (p1, p2) in enumerate(_SKELETON):
        if scores[p1] > thr and scores[p2] > thr:
            cv.line(disp, tuple(kps_px[p1]), tuple(kps_px[p2]),
                    _SKELETON_COLORS[i % len(_SKELETON_COLORS)], 2)
    for (x, y), s in zip(kps_px, scores):
        if s > thr:
            cv.circle(disp, (int(x), int(y)), 5, (0, 0, 0), -1)        # 黒縁
            cv.circle(disp, (int(x), int(y)), 3, (255, 255, 255), -1)  # 白丸
    return disp
