# SMT detector A/B — proxy vs reactive fractal (as an index entry gate)

Indices ON + frequency levers. Three arms: no SMT gate / proxy-SMT-required / fractal-SMT-required. **A gate is worth it if it lifts WR/PF without gutting trades; fractal wins if it beats proxy.**

_run commit: `6511767`_

## IS 2022-23

| arm | trades | WR% | PF | MaxDD% |
|---|---|---|---|---|
| no SMT gate | 543 | 43.10 | 2.74 | -12.76 |
| proxy SMT gate | 430 | 44.40 | 3.06 | -12.76 |
| fractal SMT gate | 440 | 44.10 | 2.79 | -12.76 |

## OOS 2024-25

| arm | trades | WR% | PF | MaxDD% |
|---|---|---|---|---|
| no SMT gate | 492 | 43.50 | 4.16 | -12.55 |
| proxy SMT gate | 437 | 44.40 | 4.71 | -12.55 |
| fractal SMT gate | 437 | 45.50 | 4.85 | -12.55 |

## How to read it

- proxy/fractal vs **no-gate**: does requiring SMT raise WR/PF? By how many trades does it cost?
- **fractal vs proxy**: higher WR/PF at similar trade count = the reactive detector is the better filter.
- Same-ballpark IS *and* OOS is the not-curve-fit check before shipping SMT as a gate.
