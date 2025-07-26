# ===== インポート =====
from __future__ import annotations

import cv2 as cv
import numpy as np
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
    (255, 255, 200),  # 明るい水色
    (255, 255, 180),
    (255, 240, 150),
    (255, 220, 140),
    (255, 255, 170),
    (230, 255, 220),
    (200, 255, 255),  # シアン
    (170, 230, 255),
    (140, 210, 255),
    (120, 200, 255),
    (80,  180, 255),  # 青寄り
    (60,  160, 255),
    (50,  140, 255),
    (40,  120, 255),
    (30,  110, 255),
    (20,  100, 255),
    (10,   90, 255),
    (0,    80, 255),
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
                    _SKELETON_COLORS[i % len(_SKELETON_COLORS)], 8)
    for (x, y), s in zip(kps_px, scores):
        if s > thr:
            cv.circle(disp, (int(x), int(y)), 16, (0, 0, 0), -1)        # 黒縁
            cv.circle(disp, (int(x), int(y)), 8, (255, 255, 255), -1)  # 白丸
    return disp
