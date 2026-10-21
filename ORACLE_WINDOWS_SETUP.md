# Running the live bot on an Oracle Cloud Windows VM (free $300 trial)

Oracle Cloud alternative to the GCP guide. The **repo scripts are identical** —
only provisioning differs. Once you're RDP'd into the Windows box, follow
`GCP_WINDOWS_SETUP.md` from **§3** (install Python/Git/MT5 → clone → run scripts);
everything from there is OS-level, not cloud-specific.

> ⚠️ **Windows on Oracle = trial credit, not "Always Free".** The Always-Free
> tier is Linux/ARM only. A Windows VM bills against the **$300 / 30-day trial
> credit**, so treat this as the box for your **DEMO phase**, not a permanent
> free live server. For long-term live hosting, the **Exness broker VPS** is the
> right home. **Stay on a DEMO account here.**

---

## 1 · Sign up for the free trial
🔗 **https://www.oracle.com/cloud/free/**

Click **Start for free** → create an account. It asks for a card for identity;
the hold is small and refundable (not an upfront charge). Pick a **home region**
near you — e.g. **UK South (London)** works well for Exness. Sign-up + verify
can take a few minutes.

## 2 · Create the Windows instance
🔗 Console → **https://cloud.oracle.com** → menu **☰ → Compute → Instances → Create instance**
(direct: **https://cloud.oracle.com/compute/instances/create**)

| Field | What to choose |
|---|---|
| **Name** | `ict-live` |
| **Image** (Edit → Change image) | **Windows Server 2022 Standard** |
| **Shape** (Edit → Change shape) | **VM.Standard.E4.Flex**, then set **2 OCPU / 8 GB** (Windows needs the RAM; the tiny Always-Free 1 GB shape can't run it) |
| **Networking** | leave "Create new virtual cloud network" — it makes a VCN + public subnet and assigns a **public IPv4** automatically |
| **Assign a public IPv4 address** | make sure this is **Yes** |
| **Boot volume** | default (~256 GB is fine on trial) |

Click **Create**. Provisioning takes ~2–3 minutes.

## 3 · Get the Windows password
On the instance's details page after it's **Running**, Oracle shows the
**initial Windows credentials once** (username — usually `opc` — and an
auto-generated password). **Copy them now.** You'll be forced to change the
password on first login. If you can't find them, use the instance's **"Reset
password"** / console-connection option in the Oracle menu.

## 4 · Open the RDP port (Oracle blocks it by default — important)
Unlike GCP, Oracle does **not** open remote-desktop port 3389 automatically. Add
one ingress rule:

1. Instance details → under **Primary VNIC**, click the **Subnet** link.
2. Open the **Default Security List** for that subnet.
3. **Add Ingress Rules** →
   - **Source CIDR:** `0.0.0.0/0` (any IP — simplest; to be safer, use *your*
     IP as `x.x.x.x/32`)
   - **IP Protocol:** **TCP**
   - **Destination Port Range:** **3389**
   - Add.

Without this rule, RDP will just time out.

## 5 · Connect via RDP
Use the instance's **Public IP address** (shown on the details page) with the
username + password from §3:
- **Laptop:** Windows "Remote Desktop Connection" (built in), or Microsoft Remote
  Desktop.
- **Phone:** install **Microsoft Remote Desktop** (free) → add PC → the public IP
  → username `opc` (or as shown) + password.

Change the password when prompted. You now have the Windows desktop.

## 6 · From here, it's identical to the GCP guide
Follow **`GCP_WINDOWS_SETUP.md` §3 onward**:
- Install **Python 3.11+** (tick "Add to PATH"), **Git**, and **MT5** (log into
  your Exness **DEMO** account; enable "Save account information").
- `git clone https://github.com/ThabisoCollinSengane/Ict.git` → `cd Ict`
- `powershell -ExecutionPolicy Bypass -File scripts\setup_vps.ps1`
- `Copy-Item live.env.example live.env` → fill in DEMO creds → smoke test.
- `scripts\install_startup_task.ps1` + enable auto-logon → hands-off 24/7.

## 7 · Protect yourself from surprise bills
- **Billing → Cost Management → Budgets:** set a budget alert (~$250) so you're
  warned before the credit runs out.
- Oracle **won't** auto-charge when the trial ends unless you manually "Upgrade
  to Pay As You Go" — the Windows VM simply stops. That's the safe default for a
  DEMO box.

---

## Which host, honestly

| Host | Free? | Good for |
|---|---|---|
| **Exness broker VPS** | free/cheap for clients | **live 24/7** (best long-term) |
| **Oracle trial** | $300 / 30 days | the **DEMO phase**, or short live trials |
| GCP trial | $300 / 90 days but wants a $10 charge | same as Oracle if you had the $10 |
| MQL5 VPS (from MT5 terminal) | ~$10–15/mo | one-click, least setup |

At R1,000 an account, don't pay monthly for hosting — use the **broker VPS** once
eligible. Oracle's trial is ideal for the required **2-week demo run** at no cost.
