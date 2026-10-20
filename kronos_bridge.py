"""P121 — thin wrapper around the Kronos K-line foundation model (github.com/shiyu-coder/Kronos).

Kronos is NOT a dependency of the engine: it is imported lazily, only when KRONOS_MODE > 0 or a
study asks for it. The repo is cloned on the runner (KRONOS_REPO, default /tmp/kronos) and its
`model` package put on sys.path; weights come from Hugging Face (NeoQuasar/*).

forecast(frames) takes a list of OHLC DataFrames of COMPLETED bars (index = bar open time, UTC,
regular spacing) and returns, per frame, the predicted close `pred_len` bars ahead minus the
last close (price units). The caller turns that into a direction. Nothing here sees a bar that
has not finished — the caller is responsible for slicing.

⚠️ Pretraining data reportedly ends June 2024 (third-party paper, not the Kronos authors), so any
result before 2024-07 may be contaminated by memorisation. CLEAN_FROM marks the honest window.
"""
import os
import sys

CLEAN_FROM = "2024-07-01"
_PRED = None


def _predictor():
    global _PRED
    if _PRED is not None:
        return _PRED
    repo = os.environ.get("KRONOS_REPO", "/tmp/kronos")
    if repo not in sys.path:
        sys.path.insert(0, repo)
    import torch
    torch.set_num_threads(int(os.environ.get("KRONOS_THREADS", os.cpu_count() or 2)))
    from model import Kronos, KronosTokenizer, KronosPredictor   # noqa: E402 (Kronos repo)
    tok = KronosTokenizer.from_pretrained(os.environ.get("KRONOS_TOKENIZER", "NeoQuasar/Kronos-Tokenizer-base"))
    mdl = Kronos.from_pretrained(os.environ.get("KRONOS_MODEL", "NeoQuasar/Kronos-small"))
    _PRED = KronosPredictor(mdl, tok, device="cpu", max_context=512)
    return _PRED


def _future_index(idx, n):
    import pandas as pd
    step = idx[-1] - idx[-2]
    return pd.Series(pd.date_range(idx[-1] + step, periods=n, freq=step))


def forecast(frames, pred_len=4, samples=5, seed=0):
    """frames: list of DataFrames with columns o/h/l/c (or open/high/low/close), naive or UTC
    DatetimeIndex. Returns list of (predicted close at pred_len) - (last close)."""
    import numpy as np
    import pandas as pd
    import torch
    torch.manual_seed(seed)
    np.random.seed(seed)
    dfs, xs, ys, last = [], [], [], []
    for f in frames:
        f = f.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close"})
        idx = f.index.tz_convert(None) if f.index.tz is not None else f.index
        dfs.append(f[["open", "high", "low", "close"]].reset_index(drop=True).astype(float))
        xs.append(pd.Series(idx))
        ys.append(_future_index(idx, pred_len))
        last.append(float(f["close"].iloc[-1]))
    p = _predictor()
    if len(dfs) == 1:
        out = [p.predict(df=dfs[0], x_timestamp=xs[0], y_timestamp=ys[0], pred_len=pred_len,
                         T=1.0, top_p=0.9, sample_count=samples, verbose=False)]
    else:
        out = p.predict_batch(df_list=dfs, x_timestamp_list=xs, y_timestamp_list=ys,
                              pred_len=pred_len, T=1.0, top_p=0.9, sample_count=samples,
                              verbose=False)
    return [float(o["close"].iloc[-1]) - lc for o, lc in zip(out, last)]
