# ===== インポート =====
# --- 標準ライブラリ ---
import urllib.request
from pathlib import Path
# ====


# ===== 定数定義 =====
DOWNLOAD_URL: str = "https://huggingface.co/Xenova/movenet-singlepose-lightning/resolve/main/onnx/model.onnx"
SAVE_PATH: str = "models/movenet_singlepose_lightning_v4.onnx"
# ====


def download_movenet_model() -> None:
    """MoveNet LightningのONNXモデルをダウンロードする。"""
    url = DOWNLOAD_URL
    out_path = Path(SAVE_PATH)

    # --- 保存先ディレクトリを作成 ---
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # --- すでにファイルがある場合はスキップ ---
    if out_path.exists():
        print(f"ファイルは既に存在します: {out_path}")
        return

    print(f"ダウンロード開始: {url}")
    urllib.request.urlretrieve(url, out_path)
    print(f"保存完了: {out_path}")


# ===== エントリポイント =====
if __name__ == "__main__":
    download_movenet_model()
