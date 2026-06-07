"""ICT Trade Chart Viewer — interactive HTML dashboard.

All filtering (pair / model / scenario / result) and pagination happen
inside the browser. Run once to generate the HTML, then open and use
the dropdowns to slice the trade set without re-running Python.

Usage:
    python scripts/chart_trades.py                        # 400 trades → data/histdata/trades_chart.html
    python scripts/chart_trades.py --years 2024 2025      # OOS only
    python scripts/chart_trades.py --max 800              # all trades
    python scripts/chart_trades.py --tf 60T               # H1 candles (default 15min)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd

DATA_DIR   = os.path.join(os.path.dirname(__file__), "..", "data", "histdata")
TRADES_CSV = os.path.join(DATA_DIR, "trades_dump.csv")

BARS_BEFORE = 50
BARS_AFTER  = 25

_EST_OFFSET = pd.Timedelta(hours=5)

_TF_ALIASES = {
    "1T": "1min",  "5T": "5min",   "15T": "15min",
    "30T": "30min","60T": "60min", "240T": "240min",
    "1H": "1h",    "4H": "4h",
}

def _norm_tf(tf: str) -> str:
    return _TF_ALIASES.get(tf, tf)

def _to_utc(t) -> pd.Timestamp:
    ts = pd.Timestamp(t)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


# ── data helpers ────────────────────────────────────────────────────────────

def _load_m1(pair: str, years: list[int]) -> pd.DataFrame:
    frames = []
    for yr in years:
        path = os.path.join(DATA_DIR, f"{pair}_{yr}.csv")
        if not os.path.exists(path):
            continue
        df = pd.read_csv(
            path, sep=";", header=None,
            names=["dt", "Open", "High", "Low", "Close", "Volume"],
            dtype={"Open": float, "High": float, "Low": float, "Close": float},
        )
        df["dt"] = pd.to_datetime(df["dt"], format="%Y%m%d %H%M%S") + _EST_OFFSET
        df = df.set_index("dt")[["Open", "High", "Low", "Close"]]
        df.index = df.index.tz_localize("UTC")
        frames.append(df)
    return pd.concat(frames).sort_index() if frames else pd.DataFrame()


def _resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    return df.resample(_norm_tf(rule)).agg(
        {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    ).dropna()


def _window(ohlc: pd.DataFrame, entry_t, exit_t) -> pd.DataFrame:
    entry_t = _to_utc(entry_t)
    exit_t  = _to_utc(exit_t)
    idx = ohlc.index
    i0  = idx.searchsorted(entry_t)
    i1  = idx.searchsorted(exit_t)
    return ohlc.iloc[max(0, i0 - BARS_BEFORE): min(len(idx), i1 + BARS_AFTER + 1)]


def _f(v):
    try:
        return None if pd.isna(v) else round(float(v), 5)
    except Exception:
        return None


def _build_trade(row, ohlc_cache: dict, tf: str) -> dict | None:
    pair = row["pair"]
    ohlc = ohlc_cache.get(pair)
    if ohlc is None or ohlc.empty:
        return None
    ohlc_tf = _resample(ohlc, tf) if _norm_tf(tf) != "1min" else ohlc
    win = _window(ohlc_tf, row["opened_at"], row["closed_at"])
    if win.empty:
        return None

    entry_t = _to_utc(row["opened_at"]).strftime("%Y-%m-%d %H:%M:%S")
    exit_t  = _to_utc(row["closed_at"]).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "pair":      str(row["pair"]),
        "direction": int(row["direction"]),
        "pnl":       round(float(row["pnl"]), 2),
        "entry":     _f(row["entry"]),
        "exit":      _f(row["exit"]),
        "stop":      _f(row.get("stop")),
        "target":    _f(row.get("target")),
        "scenario":  str(row.get("im_scenario", "")),
        "model":     str(row.get("entry_model", "")),
        "draw":      int(row.get("draw_score", 0) or 0),
        "conf":      int(row.get("target_confluence", 0) or 0),
        "crt":       str(row.get("crt_tf", "") or ""),
        "entry_t":   entry_t,
        "exit_t":    exit_t,
        "opened_at": str(row["opened_at"])[:16],
        "closed_at": str(row["closed_at"])[:16],
        "tf":        tf.replace("min", "M"),
        "ohlc": {
            "x": [t.strftime("%Y-%m-%d %H:%M:%S") for t in win.index],
            "o": [round(v, 5) for v in win["Open"]],
            "h": [round(v, 5) for v in win["High"]],
            "l": [round(v, 5) for v in win["Low"]],
            "c": [round(v, 5) for v in win["Close"]],
        },
    }


# ── HTML template ────────────────────────────────────────────────────────────

_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ICT Trade Viewer</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0d1117;color:#c9d1d9;font-family:ui-monospace,monospace;font-size:13px}

#topbar{
  background:#161b22;border-bottom:1px solid #30363d;
  padding:10px 14px;position:sticky;top:0;z-index:200
}
#topbar h1{font-size:14px;color:#58a6ff;margin-bottom:9px}

#filters{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
#filters select{
  background:#21262d;color:#c9d1d9;border:1px solid #30363d;
  padding:5px 9px;border-radius:6px;font-size:12px;cursor:pointer;min-width:130px
}
#filters select:focus{outline:none;border-color:#58a6ff}

#stats{margin-top:7px;font-size:11px;color:#8b949e}

#charts{padding:12px 14px}

.card{
  border-radius:8px;margin-bottom:14px;overflow:hidden;
  border:1px solid #21262d
}
.card.win {border-left:3px solid #3fb950}
.card.loss{border-left:3px solid #f85149}

.card-hdr{
  padding:7px 11px;display:flex;flex-wrap:wrap;gap:6px;
  align-items:center;background:#161b22;border-bottom:1px solid #21262d
}
.badge{padding:2px 7px;border-radius:4px;font-weight:700;font-size:11px}
.bwin {background:rgba(63,185,80,.2);color:#3fb950}
.bloss{background:rgba(248,81,73,.2);color:#f85149}
.blong{background:rgba(88,166,255,.15);color:#58a6ff}
.bshrt{background:rgba(255,166,88,.15);color:#ffa657}
.tag{background:#21262d;padding:2px 6px;border-radius:4px;font-size:11px;color:#8b949e}
.ppos{color:#3fb950;font-weight:700}
.pneg{color:#f85149;font-weight:700}
.dt{color:#6e7681;font-size:11px;margin-left:auto}

.chart-box{height:270px;background:#161b22}

#pgbar{
  display:flex;justify-content:center;align-items:center;gap:12px;
  padding:12px;background:#0d1117;border-top:1px solid #21262d;
  position:sticky;bottom:0
}
#pgbar button{
  background:#21262d;color:#c9d1d9;border:1px solid #30363d;
  padding:5px 15px;border-radius:6px;cursor:pointer;font-size:12px
}
#pgbar button:hover{border-color:#58a6ff}
#pgbar button:disabled{opacity:.3;cursor:default}
#pginfo{color:#8b949e;font-size:12px;min-width:180px;text-align:center}

/* legend strip */
#legend{
  display:flex;flex-wrap:wrap;gap:10px;padding:6px 14px;
  background:#0d1117;border-bottom:1px solid #21262d;font-size:11px;color:#8b949e
}
.leg{display:flex;align-items:center;gap:4px}
.lline{display:inline-block;width:22px;height:2px;border-radius:1px}
</style>
</head>
<body>

<div id="topbar">
  <h1>ICT Strategy — Trade Chart Viewer</h1>
  <div id="filters">
    <select id="fp">
      <option value="">All Pairs</option>
      <option>EURUSD</option><option>GBPUSD</option><option>NZDUSD</option>
    </select>
    <select id="fm">
      <option value="">All Entry Models</option>
      <option value="judas">Judas Reversal</option>
      <option value="breakout">Breakout</option>
    </select>
    <select id="fs"></select>
    <select id="fr">
      <option value="">All Results</option>
      <option value="win">Wins Only ✓</option>
      <option value="loss">Losses Only ✗</option>
    </select>
    <select id="fpp">
      <option value="10">10 / page</option>
      <option value="20" selected>20 / page</option>
      <option value="50">50 / page</option>
    </select>
  </div>
  <div id="stats"></div>
</div>

<div id="legend">
  <span class="leg"><span class="lline" style="background:#e3b341;border-top:2px dotted #e3b341"></span>Entry level</span>
  <span class="leg"><span class="lline" style="background:#f85149;border-top:2px dashed #f85149"></span>Stop loss</span>
  <span class="leg"><span class="lline" style="background:#58a6ff;border-top:2px dotted #58a6ff"></span>Target</span>
  <span class="leg">▲▼ = entry bar &nbsp; ✕ = exit bar</span>
  <span class="leg" style="color:#3fb950">■ green candle = bullish</span>
  <span class="leg" style="color:#8b949e">■ dark candle = bearish</span>
</div>

<div id="charts"></div>

<div id="pgbar">
  <button id="bprev" onclick="go(-1)">◀ Prev</button>
  <span id="pginfo"></span>
  <button id="bnext" onclick="go(1)">Next ▶</button>
</div>

<script>
const ALL = __DATA__;

// Build scenario dropdown from data
const scens = [...new Set(ALL.map(t=>t.scenario).filter(Boolean))].sort();
const fsel  = document.getElementById('fs');
fsel.innerHTML = '<option value="">All Scenarios</option>' +
  scens.map(s=>`<option value="${s}">${s}</option>`).join('');

let page = 1;
let vis  = ALL;

function filt(){
  const p = document.getElementById('fp').value;
  const m = document.getElementById('fm').value;
  const s = document.getElementById('fs').value;
  const r = document.getElementById('fr').value;
  vis = ALL.filter(t=>{
    if(p && t.pair!==p) return false;
    if(m && t.model!==m) return false;
    if(s && t.scenario!==s) return false;
    if(r==='win'  && t.pnl<=0) return false;
    if(r==='loss' && t.pnl>0)  return false;
    return true;
  });
  page=1; render();
}

['fp','fm','fs','fr','fpp'].forEach(id=>
  document.getElementById(id).addEventListener('change', filt));

function pp(){ return +document.getElementById('fpp').value }
function tp(){ return Math.max(1,Math.ceil(vis.length/pp())) }
function go(d){ page=Math.max(1,Math.min(tp(),page+d)); render(); }

function render(){
  const start=(page-1)*pp();
  const slice=vis.slice(start,start+pp());

  const wins=vis.filter(t=>t.pnl>0).length;
  const totpnl=vis.reduce((s,t)=>s+t.pnl,0);
  document.getElementById('stats').textContent=
    `${vis.length} of ${ALL.length} trades  ·  `+
    `${wins} wins / ${vis.length-wins} losses  ·  `+
    `Total P&L: R${totpnl>=0?'+':''}${totpnl.toFixed(0)}`;

  const box=document.getElementById('charts');
  box.innerHTML='';

  slice.forEach((t,i)=>{
    const win=t.pnl>0, lng=t.direction>0;
    const pnlHtml=win
      ?`<span class="ppos">R+${t.pnl.toFixed(0)}</span>`
      :`<span class="pneg">R${t.pnl.toFixed(0)}</span>`;

    const card=document.createElement('div');
    card.className='card '+(win?'win':'loss');
    const cid='c'+i;

    card.innerHTML=`
      <div class="card-hdr">
        <span class="badge ${win?'bwin':'bloss'}">${win?'✓ WIN':'✗ LOSS'}</span>
        <span class="badge ${lng?'blong':'bshrt'}">${lng?'▲ LONG':'▼ SHORT'}</span>
        <strong>${t.pair}</strong>
        ${pnlHtml}
        <span class="tag">[${t.tf}]</span>
        <span class="tag">${t.scenario}</span>
        <span class="tag">${t.model}</span>
        <span class="tag">draw&nbsp;${t.draw}/3</span>
        <span class="tag">conf&nbsp;${t.conf}</span>
        ${t.crt?`<span class="tag">CRT&nbsp;${t.crt}</span>`:''}
        <span class="dt">${t.opened_at} → ${t.closed_at}</span>
      </div>
      <div id="${cid}" class="chart-box"></div>`;
    box.appendChild(card);

    /* ── Plotly chart ── */
    const x0=t.ohlc.x[0], x1=t.ohlc.x[t.ohlc.x.length-1];
    const shapes=[];
    if(t.entry!=null) shapes.push({type:'line',x0,x1,y0:t.entry,y1:t.entry,
      line:{color:'#e3b341',width:1,dash:'dot'}});
    if(t.stop!=null)  shapes.push({type:'line',x0,x1,y0:t.stop,y1:t.stop,
      line:{color:'#f85149',width:1.5,dash:'dash'}});
    if(t.target!=null) shapes.push({type:'line',x0,x1,y0:t.target,y1:t.target,
      line:{color:'#58a6ff',width:1.5,dash:'dot'}});

    // entry→exit shaded zone
    if(t.entry!=null && t.exit!=null){
      shapes.push({type:'rect',x0:t.entry_t,x1:t.exit_t,
        y0:Math.min(t.entry,t.exit)*0.99995,
        y1:Math.max(t.entry,t.exit)*1.00005,
        fillcolor:win?'rgba(63,185,80,0.08)':'rgba(248,81,73,0.08)',
        line:{width:0}});
    }

    const entryPx = lng ? -16 : 16;
    const anns=[
      {x:t.entry_t, y:t.entry, text:lng?'▲':'▼', showarrow:false,
       font:{size:16,color:lng?'#3fb950':'#f85149'}, yshift:entryPx},
      {x:t.exit_t,  y:t.exit,  text:'✕', showarrow:false,
       font:{size:13,color:win?'#3fb950':'#f85149'}},
    ];

    Plotly.newPlot(cid,[{
      type:'candlestick',
      x:t.ohlc.x, open:t.ohlc.o, high:t.ohlc.h, low:t.ohlc.l, close:t.ohlc.c,
      increasing:{line:{color:'#3fb950',width:1},fillcolor:'#3fb950'},
      decreasing:{line:{color:'#4d5360',width:1},fillcolor:'#1c2030'},
      showlegend:false, hoverinfo:'x+y',
    }],{
      margin:{l:58,r:6,t:4,b:28},
      paper_bgcolor:'#161b22', plot_bgcolor:'#161b22',
      font:{color:'#6e7681',size:9},
      xaxis:{rangeslider:{visible:false},gridcolor:'#21262d',
             tickfont:{size:9},zeroline:false,showline:false},
      yaxis:{gridcolor:'#21262d',tickfont:{size:9},
             zeroline:false,showline:false,tickformat:'.5f'},
      shapes, annotations:anns, showlegend:false,
    },{displayModeBar:false,responsive:true});
  });

  document.getElementById('bprev').disabled=(page<=1);
  document.getElementById('bnext').disabled=(page>=tp());
  document.getElementById('pginfo').textContent=
    `Page ${page} of ${tp()}  (${vis.length} trades)`;
  window.scrollTo(0,0);
}

render();
</script>
</body>
</html>
"""


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="ICT interactive trade chart viewer")
    ap.add_argument("--years", nargs="+", type=int, default=[2022, 2023, 2024, 2025])
    ap.add_argument("--tf",    default="15min", help="Candle timeframe (default 15min)")
    ap.add_argument("--max",   type=int, default=400,
                    help="Max trades to embed (default 400; use 800 for all)")
    ap.add_argument("--out",   default=os.path.join(DATA_DIR, "trades_chart.html"))
    args = ap.parse_args()

    if not os.path.exists(TRADES_CSV):
        print(f"ERROR: {TRADES_CSV} not found — run run_backtest_histdata.py first")
        sys.exit(1)

    df = pd.read_csv(TRADES_CSV, parse_dates=["opened_at", "closed_at"])
    df["opened_at"] = pd.to_datetime(df["opened_at"], utc=True, errors="coerce")
    df["closed_at"] = pd.to_datetime(df["closed_at"], utc=True, errors="coerce")
    df = df.dropna(subset=["opened_at", "closed_at"])
    if args.years:
        df = df[df["opened_at"].dt.year.isin(args.years)]
    df = df.head(args.max)

    pairs_needed = df["pair"].unique().tolist()
    ohlc_cache: dict[str, pd.DataFrame] = {}
    for pair in pairs_needed:
        print(f"Loading {pair} M1 data...")
        raw = _load_m1(pair, args.years)
        if raw.empty:
            print(f"  WARNING: no CSV found for {pair} — those trades will be skipped")
        else:
            norm = _norm_tf(args.tf)
            ohlc_cache[pair] = _resample(raw, norm) if norm != "1min" else raw
            print(f"  {pair}: {len(ohlc_cache[pair]):,} {args.tf} bars")

    print(f"Building chart data for {len(df)} trades...")
    trades, skipped = [], 0
    for _, row in df.iterrows():
        t = _build_trade(row, ohlc_cache, args.tf)
        if t:
            trades.append(t)
        else:
            skipped += 1
    if skipped:
        print(f"  Skipped {skipped} trades (OHLC data missing for that date)")
    print(f"  {len(trades)} trades ready")

    data_js = json.dumps(trades).replace("</script>", r"<\/script>")
    html    = _HTML.replace("__DATA__", data_js)

    out = os.path.abspath(args.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(out) / 1_000_000
    print(f"\nSaved → {out}  ({size_mb:.1f} MB)")
    print("Open in browser. Use the dropdowns to filter by pair / model / scenario / result.")
    print("Pagination buttons at the bottom. 20 trades per page by default.")


if __name__ == "__main__":
    main()
