#!/usr/bin/env bash
# P121: install Kronos (CPU) on a GitHub runner and prove it loads + forecasts once.
set -e
pip install -q torch --index-url https://download.pytorch.org/whl/cpu
pip install -q einops "huggingface_hub==0.33.1" safetensors tqdm
[ -d /tmp/kronos ] || git clone -q --depth 1 https://github.com/shiyu-coder/Kronos.git /tmp/kronos
python - <<'PY'
import time, numpy as np, pandas as pd, kronos_bridge
idx = pd.date_range("2024-07-01", periods=400, freq="60min", tz="UTC")
c = 1.10 + np.cumsum(np.random.default_rng(0).normal(0, 0.0008, 400)); o = np.r_[c[0], c[:-1]]
f = pd.DataFrame({"o": o, "h": np.maximum(o, c) + 3e-4, "l": np.minimum(o, c) - 3e-4, "c": c}, index=idx)
t = time.time(); m = kronos_bridge.forecast([f, f, f], pred_len=4, samples=5)
print("KRONOS SMOKE OK", [round(x * 1e4, 1) for x in m], f"{time.time() - t:.1f}s per batch of 3")
PY
