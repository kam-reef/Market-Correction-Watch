# Market Risk Monitor

A quiet, rules‑based system for monitoring **broad market risk conditions** and
guiding **long‑term contribution allocation decisions** — not trading.

This project runs automatically once per week, evaluates a small set of
high‑signal market indicators, and publishes a **single, human‑readable risk
state**:

- **NOMINAL**
- **DOWNTURN**
- **RECOVERY**

The output is a static web page and (optionally) GitHub Issues when meaningful changes occur.

---

## ✅ Design Principles

- **Signal over noise**  
  Only slow‑moving, high‑level indicators are used.

- **Allocation guidance, not trading signals**  
  The system informs *where new contributions go*, not when to buy or sell.

- **Persistence matters**  
  Signals must persist across weeks to be considered meaningful.

- **Accessibility first**  
  No reliance on color, charts, or visual gimmicks.

- **Automation with human control**  
  A manual override is always available.

---

## ✅ What the System Monitors

The system evaluates a small, deliberately chosen set of indicators:

- **Trend health** (SPY 200‑day MA, QQQ 100‑day MA)
- **Risk appetite** (ARKK drawdowns and recoveries)
- **Market stress** (VIX thresholds)
- **Credit conditions** (HYG and IEF behavior)

Indicators are evaluated weekly using daily closing data.

---

## ✅ Risk States

### NOMINAL
- No sustained risk or recovery signals
- Normal market conditions

### DOWNTURN
- Multiple risk‑rising indicators active
- Signals must persist across weeks
- Used to tilt *new contributions* defensively

### RECOVERY
- Risk normalization indicators active
- Trend confirmation required
- Allocation reversion should be gradual

---

## ✅ How It Works

1. **Weekly schedule**  
   Runs Fridays at 22:00 UTC (after U.S. market close).

2. **Data fetch**  
   Daily price data is pulled from free public sources.

3. **Alert evaluation**  
   Each indicator is evaluated against fixed rules.

4. **State determination**  
   Alerts are aggregated into a single risk state with severity and persistence.

5. **Output**
   - `state_snapshot.json` (authoritative state)
   - `state_history.csv` (historical context)
   - Static web dashboard (GitHub Pages)

6. **Optional alerting**
   - GitHub Issues are created only when:
     - The risk state changes, or
     - Severity increases

---

## ✅ Manual Override

A manual override is available for:

- Market holidays
- Data issues
- Maintenance
- Judgment calls

To enable, edit config/override.json:

```json
{
  "enabled": true,
  "state": "NOMINAL",
  "severity": 0,
  "message": "Manual override enabled. Automated signals temporarily paused."
}