# Running the live bot on an Azure Windows VM

The Azure path for the always-on Windows VM that runs the MetaTrader 5 terminal +
the ICT bot. It reuses the repo's live tooling (`live/run_live.py`,
`scripts/setup_vps.ps1`, `scripts/run_live.ps1`, `scripts/install_startup_task.ps1`)
and adds a one-shot installer plus Azure-specific connect/security steps.

> ⚠️ **DEMO first.** Run on an Exness **DEMO** account for at least 2 weeks
> before funding a cent. This guide gets the machine running; it does not
> shortcut that discipline. See the go-live checklist at the bottom.

---

## What it costs against the $200 credit

| VM size | vCPU / RAM | ~cost/mo (Windows incl.) | $200 lasts |
|---|---|---|---|
| **B2s** | 2 / 4 GB | ~$60–70 | ~1 month* |
| B2ms | 2 / 8 GB | ~$85–95 | ~3 weeks* |

\* The **$200 credit expires 30 days after signup** regardless of spend, so treat
it as **one free month to get everything working**, then move to a permanent host
(Contabo/IONOS ~$5–10/mo, or the Exness free VPS once you qualify). A live bot
must stay **on 24/7**, so budget for continuous run. **B2s is the right size.**

---

## 1 · Connect via RDP

You've already created the VM and downloaded the `.rdp` file. Its contents:

```
full address:  4.222.216.84:3389
username:      Ictalgo
```

- **Password:** the one **you set when you created the VM** (Azure does not store
  it in the `.rdp` file, and no one else can read it). Forgot it? Azure Portal →
  your VM → **Help → Reset password**.
- Double-click the `.rdp` file (Windows) or use **Microsoft Remote Desktop** (Mac
  / iOS / Android): add host `4.222.216.84`, user `Ictalgo`, your password.

### 🔒 Lock down RDP before anything else

Azure's default rule opens port 3389 to the **whole internet** — that's a
constant brute-force target. Restrict it to your own IP:

1. Portal → your VM → **Networking → Network settings**.
2. Find the inbound rule for **RDP / port 3389** → edit **Source** from `Any` to
   **My IP address** → Save.
3. Also set a **long, unique password** on the `Ictalgo` account.

(If your home IP changes, just re-edit that rule.)

---

## 2 · One-shot environment bootstrap

Open an **Administrator PowerShell** on the VM (Start → right-click PowerShell →
*Run as administrator*) and paste:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
iwr https://raw.githubusercontent.com/ThabisoCollinSengane/Ict/claude/algorithm-ict-2022-alignment-9kkLi/scripts/bootstrap_vps.ps1 -OutFile $env:TEMP\bootstrap_vps.ps1 -UseBasicParsing
& $env:TEMP\bootstrap_vps.ps1
```

That installs **Chocolatey → Python → Git**, downloads the **MetaTrader 5**
installer to the Desktop, clones the repo to **`C:\ICT`** on the live branch, and
builds the **Python venv + live dependencies**. ~10–15 min. Safe to re-run.

> If the raw download is blocked for any reason, just create a file called
> `bootstrap_vps.ps1`, paste the contents from `scripts/bootstrap_vps.ps1` in the
> repo (RDP clipboard copy/paste works), and run it.

---

## 3 · Install MT5 + log into Exness

1. Run **`mt5setup.exe`** from your Desktop. Finish the install.
2. Launch MT5, **log into your Exness DEMO account**. Exness shows the exact
   **server name** (e.g. `Exness-MT5Trial14`) in the account panel — note it.
3. **Tools → Options → Server** → tick **"Keep personal settings and data at
   startup"** and **"Save account information"** so it auto-logs-in after a reboot.
4. Note the path to **`terminal64.exe`** (usually
   `C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe`).

---

## 4 · Fill in credentials

```powershell
cd C:\ICT
notepad live.env
```

Fill your **DEMO** `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER`, the
`MT5_TERMINAL_PATH`, and (recommended) Telegram `TELEGRAM_BOT_TOKEN` +
`TELEGRAM_CHAT_ID` so you get trade/halt pings on your phone. `live.env` is
git-ignored — it never leaves the machine.

---

## 5 · Smoke test (places NO trades)

```powershell
cd C:\ICT
Get-Content live.env | % { if($_ -match '^\s*([^#=][^=]*?)\s*=\s*(.*?)\s*$'){[Environment]::SetEnvironmentVariable($matches[1],$matches[2],'Process')} }
.\.venv\Scripts\python.exe -m live.smoke_test
```

A healthy run prints your account, every symbol resolved (incl. any Exness suffix
like `EURUSDm`), bars on each timeframe, a live tick, and a synthetic DXY ~90–115.
If a symbol shows `*** MISSING ***`, paste me the output and I'll fix the mapping.

Test Telegram too (optional): `.\.venv\Scripts\python.exe -m scripts.notify` →
a "test OK" message should hit your phone.

---

## 6 · Run it, and make it auto-start

Run the full bot once (Ctrl-C to stop):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_live.ps1
```

It loads `live.env`, launches MT5 if needed, and runs in a **restart-on-crash
loop**, logging to `data\live.log`. Then register auto-start at logon:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_startup_task.ps1
Start-ScheduledTask -TaskName ICTLiveBot
```

---

## 7 · Survive reboots (Windows auto-logon)

The task triggers **at logon**, so after a reboot the VM must log in itself:

1. `Win+R` → `netplwiz` → Enter.
2. Untick **"Users must enter a user name and password to use this computer"** →
   Apply → enter the `Ictalgo` username + password.

(If your image hides that checkbox, tell me and I'll give the registry
equivalent.) After a reboot: auto-logon → task fires → MT5 launches → bot
reconnects. Hands-off.

---

## 8 · Living with it

- **Done for the day? Just close the RDP window — do NOT "Log off."** Closing RDP
  *disconnects* but keeps MT5 + the bot alive. "Log off" kills them.
- **Monitor from your phone** via Telegram alerts — no need to RDP in.
- **Logs:** `Get-Content C:\ICT\data\live.log -Tail 50`.
- **Update the bot:** RDP in → `cd C:\ICT; git pull` →
  `Stop-ScheduledTask -TaskName ICTLiveBot; Start-ScheduledTask -TaskName ICTLiveBot`.
- **Stop trading now:** `Stop-ScheduledTask -TaskName ICTLiveBot` (and close any
  open positions in the MT5 terminal).

---

## Go-live checklist (do not skip)

1. Smoke test passes (§5).
2. Bot runs on **DEMO** for **≥2 weeks** without crashing; reconcile a few fills
   and any `⚠️ FEED STALE` events against `data\live.log`.
3. **Before day 30**, decide the permanent host (the $200 credit expires).
4. Only then switch `live.env` to your funded account and start at your R1,000.
