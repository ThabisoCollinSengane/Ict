"""ICT Trade Chart Viewer — interactive HTML dashboard.

All filtering and pagination happen in the browser.
Run once to generate the HTML, then open and use the dropdowns.

Usage:
    python scripts/chart_trades.py                   # 400 trades default
    python scripts/chart_trades.py --years 2024 2025
    python scripts/chart_trades.py --max 800         # all trades
    python scripts/chart_trades.py --tf 60T          # H1 candles
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


# ── entry-type parser ────────────────────────────────────────────────────────

def _parse_entry_pattern(entry_type: str) -> str:
    t = (entry_type or "").lower()
    pattern = ("FVG"     if "fvg"     in t else
               "OB"      if "ob"      in t else
               "Breaker" if "breaker" in t else "")
    tf = next((s.upper() for s in ["h4","h1","m15","m5","m1"] if s in t), "")
    return f"{pattern} {tf}".strip()


# ── data helpers ─────────────────────────────────────────────────────────────

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


def _build_trade(row, ohlc_cache: dict, tf: str, pyramid_rows=None) -> dict | None:
    pair = row["pair"]
    ohlc = ohlc_cache.get(pair)
    if ohlc is None or ohlc.empty:
        return None
    # Extend window to cover all pyramid legs too
    closed_at = row["closed_at"]
    if pyramid_rows:
        for pr in pyramid_rows:
            if pd.notna(pr["closed_at"]):
                closed_at = max(closed_at, pr["closed_at"])
    win = _window(ohlc, row["opened_at"], closed_at)
    if win.empty:
        return None

    entry_t = _to_utc(row["opened_at"]).strftime("%Y-%m-%d %H:%M:%S")
    exit_t  = _to_utc(row["closed_at"]).strftime("%Y-%m-%d %H:%M:%S")

    # Build pyramid leg data for chart overlay
    pyrs = []
    if pyramid_rows:
        for pr in pyramid_rows:
            try:
                pyrs.append({
                    "leg_idx": int(pr.get("leg_idx", 2)),
                    "entry":   _f(pr["entry"]),
                    "stop":    _f(pr.get("stop")),
                    "exit":    _f(pr["exit"]),
                    "pnl":     round(float(pr["pnl"]), 2),
                    "entry_t": _to_utc(pr["opened_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "exit_t":  _to_utc(pr["closed_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                })
            except Exception:
                pass

    total_pnl = round(float(row["pnl"]) + sum(p["pnl"] for p in pyrs), 2)

    return {
        # core
        "pair":        str(row["pair"]),
        "direction":   int(row["direction"]),
        "pnl":         round(float(row["pnl"]), 2),
        "total_pnl":   total_pnl,
        "entry":       _f(row["entry"]),
        "exit":        _f(row["exit"]),
        "stop":        _f(row.get("stop")),
        "target":      _f(row.get("target")),
        # classification
        "scenario":    str(row.get("im_scenario", "") or ""),
        "model":       str(row.get("entry_model", "") or ""),
        "pattern":     _parse_entry_pattern(str(row.get("entry_type", "") or "")),
        "draw":        int(row.get("draw_score", 0) or 0),
        "conf":        int(row.get("target_confluence", 0) or 0),
        "crt":         str(row.get("crt_tf", "") or ""),
        "target_type": str(row.get("target_type", "") or ""),
        # session
        "profile":     str(row.get("profile", "") or ""),
        "phase":       str(row.get("session_phase", "") or ""),
        # market structure
        "ms_tf":       str(row.get("mstruct_intact_tf", "") or ""),
        "ms_align":    str(row.get("mstruct_align", "") or ""),
        "ms_sweep":    bool(row.get("mstruct_minor_sweep", False)),
        "ms_pts":      int(row.get("mstruct_pts", 0) or 0),
        "ms_dir":      int(row.get("mstruct_htf_dir", 0) or 0),
        # HTF FVG
        "htf_fvg":     str(row.get("htf_fvg", "") or ""),
        # timing
        "entry_t":     entry_t,
        "exit_t":      exit_t,
        "opened_at":   str(row["opened_at"])[:16],
        "closed_at":   str(row["closed_at"])[:16],
        "tf":          tf.replace("min", "M"),
        # pyramids
        "pyramids":    pyrs,
        "has_pyramid": len(pyrs) > 0,
        # ohlc window
        "ohlc": {
            "x": [t.strftime("%Y-%m-%d %H:%M:%S") for t in win.index],
            "o": [round(v, 5) for v in win["Open"]],
            "h": [round(v, 5) for v in win["High"]],
            "l": [round(v, 5) for v in win["Low"]],
            "c": [round(v, 5) for v in win["Close"]],
        },
    }


# ── HTML template ─────────────────────────────────────────────────────────────

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

#topbar{background:#161b22;border-bottom:1px solid #30363d;
  padding:10px 14px;position:sticky;top:0;z-index:200}
#topbar h1{font-size:14px;color:#58a6ff;margin-bottom:9px}

#filters{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
#filters select{
  background:#21262d;color:#c9d1d9;border:1px solid #30363d;
  padding:5px 9px;border-radius:6px;font-size:12px;cursor:pointer;min-width:120px}
#filters select:focus{outline:none;border-color:#58a6ff}

#stats{margin-top:7px;font-size:11px;color:#8b949e}

#legend{display:flex;flex-wrap:wrap;gap:10px;padding:6px 14px;
  background:#0d1117;border-bottom:1px solid #21262d;font-size:11px;color:#8b949e}
.leg{display:flex;align-items:center;gap:5px}
.lbox{display:inline-block;width:14px;height:10px;border-radius:2px}
.ldash{display:inline-block;width:22px;height:0;border-top:2px dashed}

#charts{padding:10px 14px}

.card{border-radius:8px;margin-bottom:14px;overflow:hidden;border:1px solid #21262d}
.card.win {border-left:3px solid #3fb950}
.card.loss{border-left:3px solid #f85149}

.card-hdr{padding:7px 10px;background:#161b22;border-bottom:1px solid #21262d}
.row1{display:flex;flex-wrap:wrap;gap:5px;align-items:center;margin-bottom:4px}
.row2{display:flex;flex-wrap:wrap;gap:5px;align-items:center}

.badge{padding:2px 7px;border-radius:4px;font-weight:700;font-size:11px}
.bwin {background:rgba(63,185,80,.2);color:#3fb950}
.bloss{background:rgba(248,81,73,.2);color:#f85149}
.blong{background:rgba(88,166,255,.15);color:#58a6ff}
.bshrt{background:rgba(255,166,88,.15);color:#ffa657}
.bswp {background:rgba(255,215,0,.15);color:#e3b341}

.tag{background:#21262d;padding:2px 6px;border-radius:4px;font-size:11px;color:#8b949e}
.tag.hi{color:#c9d1d9}
.ppos{color:#3fb950;font-weight:700}
.pneg{color:#f85149;font-weight:700}
.dt{color:#6e7681;font-size:10px;margin-left:auto}

.chart-box{height:260px;background:#161b22}

#pgbar{display:flex;justify-content:center;align-items:center;gap:12px;
  padding:10px;background:#0d1117;border-top:1px solid #21262d;
  position:sticky;bottom:0}
#pgbar button{background:#21262d;color:#c9d1d9;border:1px solid #30363d;
  padding:5px 15px;border-radius:6px;cursor:pointer;font-size:12px}
#pgbar button:hover{border-color:#58a6ff}
#pgbar button:disabled{opacity:.3;cursor:default}
#pginfo{color:#8b949e;font-size:12px;min-width:180px;text-align:center}
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
    <select id="fpat"></select>
    <select id="fprof">
      <option value="">All Sessions</option>
      <option value="london">London</option>
      <option value="ny">NY AM</option>
    </select>
    <select id="fr">
      <option value="">All Results</option>
      <option value="win">Wins ✓</option>
      <option value="loss">Losses ✗</option>
    </select>
    <select id="fpyram">
      <option value="">All Legs</option>
      <option value="yes">Has Pyramids</option>
      <option value="no">No Pyramid</option>
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
  <span class="leg"><span class="lbox" style="background:rgba(255,215,0,0.15)"></span>London KZ 08-10 UTC</span>
  <span class="leg"><span class="lbox" style="background:rgba(88,166,255,0.1)"></span>NY AM KZ 12-15 UTC</span>
  <span class="leg"><span class="ldash" style="border-color:#e3b341"></span>Entry level</span>
  <span class="leg"><span class="ldash" style="border-color:#f85149"></span>Stop</span>
  <span class="leg"><span class="ldash" style="border-color:#58a6ff;border-style:dotted"></span>Target</span>
  <span class="leg">▲▼ L1 entry &nbsp; ✕ exit</span>
  <span class="leg" style="color:#00bcd4">▲▼ L2 pyramid</span>
  <span class="leg" style="color:#ce93d8">▲▼ L3 pyramid</span>
  <span class="leg" style="color:#3fb950">■ green=bullish</span>
  <span class="leg" style="color:#4d5360">■ dark=bearish</span>
</div>

<div id="charts"></div>

<div id="pgbar">
  <button id="bprev" onclick="go(-1)">◀ Prev</button>
  <span id="pginfo"></span>
  <button id="bnext" onclick="go(1)">Next ▶</button>
</div>

<script>
const ALL = __DATA__;

// populate dynamic dropdowns
function makeOpts(sel, vals, label){
  sel.innerHTML=`<option value="">${label}</option>`+
    [...new Set(vals.filter(Boolean))].sort().map(v=>`<option value="${v}">${v}</option>`).join('');
}
makeOpts(document.getElementById('fs'),  ALL.map(t=>t.scenario), 'All Scenarios');
makeOpts(document.getElementById('fpat'),ALL.map(t=>t.pattern),  'All Patterns');

let page=1, vis=ALL;

function filt(){
  const p  = document.getElementById('fp').value;
  const m  = document.getElementById('fm').value;
  const s  = document.getElementById('fs').value;
  const pt = document.getElementById('fpat').value;
  const pr = document.getElementById('fprof').value;
  const r  = document.getElementById('fr').value;
  const py = document.getElementById('fpyram').value;
  vis = ALL.filter(t=>{
    if(p  && t.pair!==p)     return false;
    if(m  && t.model!==m)    return false;
    if(s  && t.scenario!==s) return false;
    if(pt && t.pattern!==pt) return false;
    if(pr && t.profile!==pr) return false;
    if(r==='win'  && t.pnl<=0)       return false;
    if(r==='loss' && t.pnl>0)        return false;
    if(py==='yes' && !t.has_pyramid) return false;
    if(py==='no'  && t.has_pyramid)  return false;
    return true;
  });
  page=1; render();
}
['fp','fm','fs','fpat','fprof','fr','fpyram','fpp'].forEach(id=>
  document.getElementById(id).addEventListener('change', filt));

function pp(){ return +document.getElementById('fpp').value }
function tp(){ return Math.max(1,Math.ceil(vis.length/pp())) }
function go(d){ page=Math.max(1,Math.min(tp(),page+d)); render(); }

// ── session zone shapes ─────────────────────────────────────────────────────
function sessionShapes(xs){
  const dates=[...new Set(xs.map(x=>x.slice(0,10)))];
  const shapes=[], anns=[];
  dates.forEach(d=>{
    // London killzone 08:00-10:00 UTC
    shapes.push({type:'rect',x0:`${d} 08:00:00`,x1:`${d} 10:00:00`,
      y0:0,y1:1,yref:'paper',layer:'below',
      fillcolor:'rgba(255,215,0,0.07)',line:{width:0}});
    // NY AM killzone 12:00-15:00 UTC
    shapes.push({type:'rect',x0:`${d} 12:00:00`,x1:`${d} 15:00:00`,
      y0:0,y1:1,yref:'paper',layer:'below',
      fillcolor:'rgba(88,166,255,0.07)',line:{width:0}});
    // vertical session open lines
    [{t:'08:00:00',lbl:'LO'},{t:'12:00:00',lbl:'NY'},{t:'00:00:00',lbl:''}].forEach(({t,lbl})=>{
      shapes.push({type:'line',x0:`${d} ${t}`,x1:`${d} ${t}`,y0:0,y1:1,yref:'paper',
        line:{color:'rgba(255,255,255,0.12)',width:1,dash:'dot'}});
      if(lbl) anns.push({x:`${d} ${t}`,y:0.97,yref:'paper',text:lbl,showarrow:false,
        font:{size:9,color:'rgba(255,255,255,0.3)'},xanchor:'left',xshift:3});
    });
  });
  return {shapes,anns};
}

// ── render page ─────────────────────────────────────────────────────────────
function render(){
  const start=(page-1)*pp();
  const slice=vis.slice(start,start+pp());

  const wins=vis.filter(t=>t.pnl>0).length;
  const totpnl=vis.reduce((s,t)=>s+t.pnl,0);
  document.getElementById('stats').textContent=
    `${vis.length} of ${ALL.length} trades  ·  `+
    `${wins} wins / ${vis.length-wins} losses  ·  `+
    `P&L: R${totpnl>=0?'+':''}${totpnl.toFixed(0)}`;

  const box=document.getElementById('charts');
  box.innerHTML='';

  slice.forEach((t,i)=>{
    const win=t.pnl>0, lng=t.direction>0;
    // Show total P&L (L1 + pyramids) if there are pyramids
    const dispPnl = t.has_pyramid ? t.total_pnl : t.pnl;
    const dispWin = dispPnl > 0;
    const pyrTag = t.has_pyramid
      ? `<span class="tag" style="color:#00bcd4">L1+${t.pyramids.length}pyr</span>` : '';
    const pnlHtml=dispWin
      ?`<span class="ppos">R+${dispPnl.toFixed(0)}</span>`
      :`<span class="pneg">R${dispPnl.toFixed(0)}</span>`;

    // row 2 tags — structure + HTF context
    const r2parts=[];
    if(t.pattern)  r2parts.push(`<span class="tag hi">${t.pattern}</span>`);
    if(t.ms_tf)    r2parts.push(`<span class="tag">Struct&nbsp;${t.ms_tf}</span>`);
    if(t.ms_sweep) r2parts.push(`<span class="badge bswp">Judas sweep</span>`);
    if(t.ms_align) r2parts.push(`<span class="tag">Align&nbsp;${t.ms_align}</span>`);
    if(t.htf_fvg)  r2parts.push(`<span class="tag">HTF-FVG&nbsp;${t.htf_fvg}</span>`);
    if(t.target_type) r2parts.push(`<span class="tag">TP&nbsp;${t.target_type}</span>`);
    if(t.phase)    r2parts.push(`<span class="tag">${t.phase}</span>`);

    const card=document.createElement('div');
    card.className='card '+(win?'win':'loss');
    const cid='c'+i;
    card.innerHTML=`
      <div class="card-hdr">
        <div class="row1">
          <span class="badge ${win?'bwin':'bloss'}">${win?'✓ WIN':'✗ LOSS'}</span>
          <span class="badge ${lng?'blong':'bshrt'}">${lng?'▲ LONG':'▼ SHORT'}</span>
          <strong>${t.pair}</strong>
          ${pnlHtml}
          <span class="tag">[${t.tf}]</span>
          <span class="tag">${t.scenario}</span>
          <span class="tag">${t.model}</span>
          ${pyrTag}
          <span class="tag">draw&nbsp;${t.draw}/3</span>
          <span class="tag">conf&nbsp;${t.conf}</span>
          ${t.crt?`<span class="tag">CRT&nbsp;${t.crt}</span>`:''}
          <span class="dt">${t.opened_at} → ${t.closed_at}</span>
        </div>
        ${r2parts.length?`<div class="row2">${r2parts.join('')}</div>`:''}
      </div>
      <div id="${cid}" class="chart-box"></div>`;
    box.appendChild(card);

    /* ── Plotly ── */
    const {shapes:szones, anns:sanns} = sessionShapes(t.ohlc.x);

    const x0=t.ohlc.x[0], x1=t.ohlc.x[t.ohlc.x.length-1];
    const lvlShapes=[];
    if(t.entry!=null) lvlShapes.push({type:'line',x0,x1,y0:t.entry,y1:t.entry,
      line:{color:'#e3b341',width:1,dash:'dot'}});
    if(t.stop!=null)  lvlShapes.push({type:'line',x0,x1,y0:t.stop,y1:t.stop,
      line:{color:'#f85149',width:1.5,dash:'dash'}});
    if(t.target!=null) lvlShapes.push({type:'line',x0,x1,y0:t.target,y1:t.target,
      line:{color:'#58a6ff',width:1.5,dash:'dot'}});

    // entry→exit trade zone
    if(t.entry!=null && t.exit!=null) lvlShapes.push({
      type:'rect',x0:t.entry_t,x1:t.exit_t,
      y0:Math.min(t.entry,t.exit)*0.99995,y1:Math.max(t.entry,t.exit)*1.00005,
      fillcolor:win?'rgba(63,185,80,0.09)':'rgba(248,81,73,0.09)',line:{width:0}});

    const tradeAnns=[
      {x:t.entry_t,y:t.entry,text:lng?'▲':'▼',showarrow:false,
       font:{size:16,color:lng?'#3fb950':'#f85149'},yshift:lng?-16:16},
      {x:t.exit_t, y:t.exit, text:'✕',showarrow:false,
       font:{size:13,color:win?'#3fb950':'#f85149'}},
    ];
    // Pyramid leg markers (L2=cyan, L3=purple)
    const pyrColors={2:'#00bcd4',3:'#ce93d8'};
    (t.pyramids||[]).forEach(p=>{
      const pc=pyrColors[p.leg_idx]||'#00bcd4';
      const pw=p.pnl>0;
      // pyramid entry level line
      lvlShapes.push({type:'line',x0:t.ohlc.x[0],x1:t.ohlc.x[t.ohlc.x.length-1],
        y0:p.entry,y1:p.entry,line:{color:pc,width:1,dash:'dashdot'}});
      // entry marker
      tradeAnns.push({x:p.entry_t,y:p.entry,
        text:lng?'▲':'▼',showarrow:false,
        font:{size:13,color:pc},yshift:lng?-13:13});
      // exit marker
      tradeAnns.push({x:p.exit_t,y:p.exit,text:'✕',showarrow:false,
        font:{size:11,color:pw?pc:'#f85149'}});
      // trade zone for pyramid
      if(p.entry!=null&&p.exit!=null) lvlShapes.push({
        type:'rect',x0:p.entry_t,x1:p.exit_t,
        y0:Math.min(p.entry,p.exit)*0.99995,y1:Math.max(p.entry,p.exit)*1.00005,
        fillcolor:pw?'rgba(0,188,212,0.06)':'rgba(248,81,73,0.06)',line:{width:0}});
    });

    Plotly.newPlot(cid,[{
      type:'candlestick',
      x:t.ohlc.x,open:t.ohlc.o,high:t.ohlc.h,low:t.ohlc.l,close:t.ohlc.c,
      increasing:{line:{color:'#3fb950',width:1},fillcolor:'#3fb950'},
      decreasing:{line:{color:'#4d5360',width:1},fillcolor:'#1c2030'},
      showlegend:false,hoverinfo:'x+y',
    }],{
      margin:{l:58,r:6,t:4,b:26},
      paper_bgcolor:'#161b22',plot_bgcolor:'#161b22',
      font:{color:'#6e7681',size:9},
      xaxis:{rangeslider:{visible:false},gridcolor:'#21262d',
             tickfont:{size:9},zeroline:false,showline:false},
      yaxis:{gridcolor:'#21262d',tickfont:{size:9},
             zeroline:false,showline:false,tickformat:'.5f'},
      shapes:[...szones,...lvlShapes],
      annotations:[...sanns,...tradeAnns],
      showlegend:false,
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
    ap.add_argument("--tf",    default="15min")
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
        print(f"Loading {pair}...")
        raw = _load_m1(pair, args.years)
        if raw.empty:
            print(f"  WARNING: no CSV for {pair} — trades will be skipped")
        else:
            norm = _norm_tf(args.tf)
            ohlc_cache[pair] = _resample(raw, norm) if norm != "1min" else raw
            print(f"  {pair}: {len(ohlc_cache[pair]):,} {args.tf} bars")

    # Group legs into positions: leg_idx=1 is the primary card,
    # leg_idx>1 are pyramids attached to the preceding L1 for the same pair+direction.
    df_s = df.sort_values("opened_at").reset_index(drop=True)
    pos_id_col = []
    cur_pos: dict = {}  # (pair, direction) -> position_id of most recent L1
    for _, row in df_s.iterrows():
        key = (row["pair"], int(row.get("leg_idx", 1) > 1 or 0),
               str(row["pair"]), int(row["direction"]))
        pk = (str(row["pair"]), int(row["direction"]))
        li = int(row.get("leg_idx", 1) or 1)
        if li == 1:
            pid = len(pos_id_col)
            cur_pos[pk] = pid
        else:
            pid = cur_pos.get(pk, len(pos_id_col))
        pos_id_col.append(pid)
    df_s["_pos_id"] = pos_id_col

    # Build pyramid lookup: pos_id -> list of pyramid rows
    pyr_map: dict[int, list] = {}
    for _, row in df_s[df_s.get("leg_idx", pd.Series(1, index=df_s.index)) > 1
                        if "leg_idx" in df_s.columns
                        else df_s.iloc[0:0]].iterrows():
        pid = int(row["_pos_id"])
        pyr_map.setdefault(pid, []).append(row)

    # Only show L1 (initial legs) as chart cards; pyramids are overlaid
    if "leg_idx" in df_s.columns:
        df_l1 = df_s[df_s["leg_idx"].fillna(1).astype(int) == 1].copy()
    else:
        df_l1 = df_s.copy()

    print(f"Building data for {len(df_l1)} positions ({len(df_s)} total legs)...")
    trades, skipped = [], 0
    for _, row in df_l1.iterrows():
        pid = int(row["_pos_id"])
        pyrs = pyr_map.get(pid, [])
        t = _build_trade(row, ohlc_cache, args.tf, pyramid_rows=pyrs if pyrs else None)
        if t:
            trades.append(t)
        else:
            skipped += 1
    if skipped:
        print(f"  Skipped {skipped} (no OHLC for that date)")
    pyr_count = sum(1 for t in trades if t["has_pyramid"])
    print(f"  {len(trades)} positions embedded ({pyr_count} with pyramids)")

    data_js = json.dumps(trades).replace("</script>", r"<\/script>")
    html    = _HTML.replace("__DATA__", data_js)

    out = os.path.abspath(args.out)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(out) / 1_000_000
    print(f"\nSaved → {out}  ({size_mb:.1f} MB)")
    print("Open in browser. Filter dropdowns at top. Pagination at bottom.")
    print("To access from phone: python scripts/serve.py")


if __name__ == "__main__":
    main()
