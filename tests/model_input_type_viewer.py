# ===== インポート =====
# --- 外部ライブラリ ---
import onnxruntime as ort
# ====


# ===== 定数定義 =====
MODEL_PATH: str = "models/movenet_singlepose_lightning_v4.onnx"
# ====


session = ort.InferenceSession(MODEL_PATH)
for inp in session.get_inputs():
    print("name:", inp.name)
    print("type:", inp.type)
    print("shape:", inp.shape)
