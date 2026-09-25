# Ops bot — run setup, backtests & the live bot from Telegram

A **second** Telegram bot that drives the VM for you — set up the trading account,
run the smoke test, start/stop the live bot, pull updates, tail logs, and run
backtests, all from your phone. It's **owner-only** and **whitelist-only** (a fixed
set of actions, never arbitrary shell), and uses its **own token** so it never
clashes with the live alert bot.

## One-time setup

1. **Create the second bot** in Telegram: @BotFather → `/newbot` → copy its token.
   Open the new bot and send it `/start` once (so it can message you).
2. **Add the token to `live.env`** on the VM:
   ```
   OPS_BOT_TOKEN=<the second bot's token>
   ```
   (Chat id is reused from `TELEGRAM_CHAT_ID` — no need to set it again.)
3. **Start it** (from `C:\ICT`):
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\ops_bot.ps1
   ```
   You'll get an **"OPS BOT ONLINE"** message. Leave that window running (or, once
   you're happy, we can register it as an auto-start task like the live bot).

After that, everything below happens from your phone.

## Commands

| Command | What it does |
|---|---|
| `/status` | What's configured + whether the live bot is running |
| `/setaccount <login> <server>` | Save MT5 login + server to `live.env` |
| `/setpassword <pwd>` | Save MT5 password (see warning) |
| `/setpath <terminal64.exe>` | Save the MT5 terminal path |
| `/smoketest` | Run the MT5 connectivity test (places NO trades) |
| `/installtask` | Register the live bot to auto-start (Windows) |
| `/startbot` · `/stopbot` | Start / stop the live trading bot |
| `/backtest [years]` | Run the backtest, send the summary back |
| `/validate <name>` | Run a validation runner (`structure_entry`, `pdliq`, …) |
| `/logs [n]` | Tail `data/live.log` |
| `/pull` | `git pull --ff-only` (update the code) |
| `/help` | The command list |

Long jobs (smoke test, backtest, validate) reply **"started…"** and then send the
result when done, so the bot stays responsive.

## Setting up the trading account from your phone

```
/setaccount 12345678 Exness-MT5Trial14
/setpassword your-demo-password
/setpath C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe
/smoketest
```
`/smoketest` confirms MT5 is reachable and every symbol resolves. Then
`/installtask` → `/startbot` brings the live bot up.

## Important notes

- **Password over Telegram:** fine for a **demo** account, but the message sits in
  Telegram history. For the **funded** account, type the password in `notepad
  live.env` on the VM instead, and delete any `/setpassword` message.
- **Backtests need the M1 data**, which lives in the Codespace, not the VM. On the
  VM `/backtest` only works if the data is present; the natural home for backtests
  is still the Codespace. `/validate` needs `bash` (Git Bash) on Windows.
- **Two bots, two jobs:** the live alert bot (`TELEGRAM_BOT_TOKEN`) handles trade
  alerts + `/lot /bias /close /halt`; this ops bot (`OPS_BOT_TOKEN`) handles setup
  and running things. Keep the tokens distinct — Telegram allows only one poller
  per bot.
- **Security:** owner-chat-only, fixed whitelist, no arbitrary shell. Rotate both
  tokens before you go live with real money, and keep them only in `live.env`
  (git-ignored).
