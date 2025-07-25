# ===== インポート =====
# --- 標準ライブラリ ---
import urllib.request
from pathlib import Path
# ====


# ===== 定数定義 =====
ONNX_PATH: str = "models/movenet_singlepose_lightning_v4.onnx"
ONNX_URL: str = "https://huggingface.co/Xenova/movenet-singlepose-lightning/resolve/main/onnx/model.onnx"
# ====


def download_movenet_onnx() -> None:
    """MoveNet LightningのONNXモデルをダウンロードする。"""
    url = ONNX_URL
    out_path = Path(ONNX_PATH)

    # --- 保存先ディレクトリを作成 ---
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # --- すでにファイルがある場合はスキップ ---
    if out_path.exists():
        print(f"ファイルは既に存在します：{out_path}")
        return

    print(f"ダウンロード開始：{url}")
    urllib.request.urlretrieve(url, out_path)
    print(f"保存完了：{out_path}")


# ===== エントリポイント =====
if __name__ == "__main__":
    download_movenet_onnx()
