# Stat-card fields used in these experiments

Where: `GLOBAL/GLOBALB.BUN` (and the same data inside `GLOBAL/GlobalB.lzc`), chunk id `0x34600`, 46 car records of **2192 bytes** each. All offsets below are **inside one record**; floats are little-endian 32-bit.

Confidence column: **doc** = described by the PS2 documentation (reference 1 in the README), **PC** = I checked it on the PC data or in `SPEED2.EXE`, **inferred** = my reading from cross-car patterns, not confirmed by any source.

| Offset | Meaning | Confidence |
|---|---|---|
| `+0x08` | car name, 32 bytes, NUL-terminated (`COROLLA`, `RX7`, ...) | PC |
| `+0x118 / +0x11c / +0x120` | centre-of-gravity offset (x forward, y, z up) from the model origin; the PC per-wheel load function subtracts the x value from the front wheel's x | doc + PC |
| `+0x128 + 0x30*i` | wheel *i*: x, y, z at +0/+4/+8, radius at +0x10, width at +0x14. Wheels 0 and 1 are the front pair. Wheelbases come out right (RX-7 2.45 m, Hummer 3.10 m) | doc + PC |
| `+0x1e8` (front) / `+0x208` (rear) | axle tyre block, 5 floats: slip-angle scale (12), load normaliser (1), lateral scale (1), **friction-circle mu**, longitudinal mu | doc |
| `+0x228` | mass in tonnes | doc |
| `+0x22c..` | body dimensions (length, width, height); RX-7 reads 4.28 x 1.75 x 1.23 | inferred |
| `+0x238..` | inertia diagonal; equals m(a^2+b^2)/12 of those dimensions | PC |
| `+0x278` | yaw-inertia scale | doc |
| `+0x288` (front) / `+0x2a8` (rear) | suspension, 8 floats: progressive term, spring rate k, damping (v>0), damping (v<=0), anti-roll, travel limits, ... | doc |
| `+0x2d0` | final drive ratio (Corolla 3.484, RX-7 4.1) | inferred |
| `+0x2d8` | rear drive share: 0 = FWD, 0.5 = AWD, 1 = RWD (the pattern separates every car) | inferred |
| `+0x308` | engine: idle, redline, max rpm | doc |
| `+0x318` | torque curve, 9 points; x1000 gives N.m (Corolla peak 130, Skyline 243, matching a remark in `PerfModel.h`) | inferred |
| `+0x378..+0x384` | aero block; the value at `+0x384` is added to wheel load multiplied by a runtime factor in the per-wheel load function (`0x598a00`). It is 0 for the Corolla in stock. The size of that factor and whether it depends on speed are **not verified** | PC (partly) |

## Performance-part targets (stage 3)

The game copies the record and blends it toward "upgrade" tables stored **in the same record**. The offsets in `PerfModel.h` are relative to that copy, which starts at `record + 0x118`; add `0x118` to use them on the record.

| Offset in the record | What | Notes |
|---|---|---|
| `+0x658` (front) / `+0x678` (rear) | axle block targets, same 5 floats as `+0x1e8`; the friction-circle mu target is the 4th float | doc; Corolla 1.85 / 1.85, RX-7 1.90 / 2.00 |
| `+0x628` | turbo torque curve, 9 points, added to the base curve | doc |
| `+0x6a8 / +0x6b8` | aero pack targets (shop category 9) | doc; which destination each float feeds is not resolved |
| `+0x6d8` (front) / `+0x6f8` (rear) | suspension targets, same 8 floats as `+0x288` | doc |

"Torque per tonne at stage 3" in the findings is my estimate: the base torque curve plus the turbo table only, divided by the mass. The other engine categories are not included.

## Tyre model used for the effective-grip figures (reconstructed, PS2 port)

- Normalised load x = 0.8 x wheel load (kN) / load normaliser; lateral force = 2.5 x curve(slip band, x); the curve is tabulated at x = 0, 2, 4, 6, 8, 10 and is concave (rows are in `UG2Vehicle.cpp`).
- The friction circle limits total force to `load x mu`.
- "Effective grip" in this repository = the smaller of (lateral force / load from the curve at the static wheel load) and the friction-circle mu. Static loads come from the weight split `a/L` using the centre-of-gravity offset. No load transfer, no drift assist: it is a static estimate, and differences of about 1 % between cars are within its noise.

## Sensitivity to aero load (static model, illustration only)

Added downforce is expressed as a fraction f of the car's weight and shared front/rear like the weight. The real f at 180 km/h is **unknown**, and f = 2 (twice the weight) is probably unrealistic. The table shows how the model's balance would move with f. It is a sensitivity illustration, not an explanation of the behaviour seen in game.

| f | Corolla front/rear grip | RX-7 front/rear grip | Corolla lateral g | RX-7 lateral g |
|---|---|---|---|---|
| 0 | 0.999 | 0.991 | 1.83 | 1.81 |
| 1.0 | 0.992 | 0.936 | 1.79 | 1.69 |
| 2.0 | 0.967 | 0.862 | 1.65 | 1.44 |

A ratio below 1 means the front axle saturates first (understeer). The RX-7 carries 58.6 % of its weight on the front axle (3.5 kN per wheel) against 54 % (2.56 kN) for the Corolla, so if the extra load were large, it would push the RX-7's front tyres into the flat part of the curve sooner.
