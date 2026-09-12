# Running the live bot 24/7 on a Google Cloud Windows VM ($300 free trial)

This is the GCP path for the always-on Windows VPS that runs the MetaTrader 5
terminal + the ICT bot around the clock. It reuses the repo's existing live
tooling (`live/run_live.py`, `scripts/setup_vps.ps1`, `LIVE_SETUP.md`) and adds
GCP provisioning + auto-start-on-boot + restart-on-crash.

> ⚠️ **DEMO first.** Run on an Exness **DEMO** account for at least 2 weeks
> before funding a cent. The strategy is validated in backtest, not yet proven
> live. This guide gets the machine running; it does not shortcut that discipline.

---

## What this costs against the $300 credit

MT5 + Windows wants ~4–8 GB RAM. A sensible box:

| Machine type | vCPU / RAM | ~cost/mo (incl. Windows license) | $300 lasts |
|---|---|---|---|
| **e2-medium** | 2 / 4 GB | ~$35–45 | ~7 months |
| e2-standard-2 | 2 / 8 GB | ~$55–65 | ~5 months (roomier) |

Windows Server licensing is baked into the per-second price (no separate license
to buy). A live bot must stay **on 24/7**, so you can't stop it to save credit —
budget for continuous run. **e2-medium is the right starting size.**

> Set a **budget alert** (Billing → Budgets & alerts → create a budget at e.g.
> $250) so you're warned before the credit runs out.

---

## 1 · Create the VM (GCP Console, ~5 min)

1. Console → **Compute Engine → VM instances → Create instance**
   (enable the Compute Engine API if prompted).
2. **Name** `ict-live`, pick a **region** near your broker's servers (Exness is
   commonly London — `europe-west2` is a good default).
3. **Machine configuration:** series **E2**, type **e2-medium**.
4. **Boot disk → Change:** Operating system **Windows Server**, version
   **Windows Server 2022 Datacenter**, disk **50 GB Balanced**. Select.
5. Leave firewall as-is (RDP 3389 is allowed to the instance by default for
   Windows images). Click **Create**.

## 2 · Set the Windows password + connect via RDP

1. When the instance is running: the VM row → **▸ RDP dropdown → Set Windows
   password** → choose a username → copy the generated password.
2. Same dropdown → **Download the RDP file** (or use any RDP client with the
   VM's external IP). On a phone, use **Microsoft Remote Desktop** (free app) —
   add the external IP, your username + password. This is your remote desktop.

## 3 · One-time installs on the VM (~15 min)

Inside the RDP session (Server Manager may nag — ignore it):

1. **Python 3.11+** — https://www.python.org/downloads/windows/ —
   during install **tick "Add python.exe to PATH."**
2. **Git** — https://git-scm.com/download/win (accept defaults).
3. **MetaTrader 5** — install from Exness, launch it, **log into your DEMO
   account**, and in the terminal enable **Tools → Options → Server → "Keep
   personal settings and data at startup"** and tick **"Save account
   information"** so it auto-logs-in after a reboot. Note the exact **server
   name** shown in the account panel.
4. In the MT5 install folder, note the path to **`terminal64.exe`** (for
   `MT5_TERMINAL_PATH` below).

## 4 · Get the repo + install deps

Open **PowerShell** and:

```powershell
git clone https://github.com/ThabisoCollinSengane/Ict.git
cd Ict
powershell -ExecutionPolicy Bypass -File scripts\setup_vps.ps1
```

`setup_vps.ps1` builds `.venv` and installs `requirements_live.txt` (MetaTrader5,
pandas, numpy, …).

## 5 · Credentials (never committed)

```powershell
Copy-Item live.env.example live.env
notepad live.env
```

Fill in your **DEMO** `MT5_LOGIN` / `MT5_PASSWORD` / `MT5_SERVER`, the
`MT5_TERMINAL_PATH`, and (recommended) your Telegram bot token + chat id.
`live.env` is git-ignored — it never leaves the machine.

## 6 · Smoke test (places NO trades)

```powershell
powershell -ExecutionPolicy Bypass -Command `
  "Get-Content live.env | % { if($_ -match '^\s*([^#=][^=]*?)\s*=\s*(.*?)\s*$'){[Environment]::SetEnvironmentVariable($matches[1],$matches[2],'Process')} }; .\.venv\Scripts\python.exe -m live.smoke_test"
```

A healthy run prints your account, every symbol resolved (incl. any Exness
suffix like `EURUSDm`), bars on each timeframe, a live tick, and a synthetic DXY
~90–115. If a symbol shows `*** MISSING ***`, tell me and I'll adjust the mapping.

## 7 · Run it, and make it auto-start

Test the full runner once (Ctrl-C to stop):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_live.ps1
```

It loads `live.env`, launches MT5 if needed, and runs the bot in a
**restart-on-crash loop**, logging to `data\live.log`. Then register auto-start:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_startup_task.ps1
Start-ScheduledTask -TaskName ICTLiveBot
```

Now the bot runs at every logon and restarts itself if it ever exits.

## 8 · Survive reboots (Windows auto-logon)

The task triggers **at logon**, so after a reboot the VM must log in
automatically. Enable auto-logon once:

1. `Win+R` → `netplwiz` → Enter.
2. Untick **"Users must enter a user name and password to use this computer"** →
   Apply → enter your Windows username + password.

(If your image hides that checkbox, tell me and I'll give you the registry
equivalent.) After a reboot the VM auto-logs-in → the task fires → MT5 launches →
the bot reconnects. Fully hands-off.

## 9 · Living with it

- **Leave it running. When you're done for the day, just close the RDP window —
  do NOT "Log off."** Closing RDP *disconnects* but keeps the session (and MT5 +
  bot) alive. "Log off" kills the GUI session and stops MT5.
- **Monitor from your phone** via the Telegram alerts (trade opened/closed,
  circuit breakers, daily/weekly equity snapshots) — no need to RDP in.
- **Check logs:** `Get-Content data\live.log -Tail 50` in PowerShell.
- **Update the bot:** RDP in → `cd Ict; git pull` → `Stop-ScheduledTask
  -TaskName ICTLiveBot; Start-ScheduledTask -TaskName ICTLiveBot`.
- **Stop trading immediately:** `Stop-ScheduledTask -TaskName ICTLiveBot` (and
  close positions in the MT5 terminal if needed).

---

## What I can and can't do from here

I can't RDP into or provision the VM for you — I have no GCP access from this
session. What I've done is make the repo a turn-key deploy: every script and the
exact commands above are in the repo, so your job on the VM is create → connect →
paste. If a step errors (a missing symbol, a Python/MT5 path, an auto-logon
checkbox that isn't there), paste me the output and I'll fix the script or give
you the workaround — same loop we've used for the Codespace runs.

## Reminder: DEMO → paper-trade → then fund

1. Smoke test passes (§6).
2. Bot runs on **DEMO** for **≥2 weeks** without crashing; reconcile a few
   trades and any `⚠️ FEED STALE` events against `data\live.log`.
3. Only then switch `live.env` to your funded account and start at your R1,000.
