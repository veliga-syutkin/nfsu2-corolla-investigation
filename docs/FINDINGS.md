# Findings: what explains the Corolla's (AE86) cornering at max parts?

## The question

Players say the Corolla corners abnormally well once it has stage 3 performance parts, understeers less than other cars, even oversteers a little without sliding, and keeps its speed. The common explanations are "it's bugged" or "it needs a mod". A secondary question: with the same unique performance packages, could the RX-7 beat it?

## Short answer

Nothing in the game's car table points to a bug. Here is what the tests support, and what they do not:

- **Demonstrated in game:** the weight distribution between the axles is a real lever (tests `control`, `rx7-52` and `swap`).
- **Plausible, but not isolated by any test:** the total mass, through the load on each wheel (front: 2.56 kN for the Corolla against 3.50 kN for the RX-7), and the aero. The aero term does exist in the game's per-wheel load function (confirmed in `SPEED2.EXE`), but its size and its dependence on speed are unknown. It is kept here as a present factor of unknown magnitude; the argument does not rest on it.
- **Two different things to keep apart:**
  - the **level of grip** (lateral g before breakaway), which in the model depends on the load per wheel, hence on the total mass (plus whatever aero adds), through the tyre's sensitivity to load. That sensitivity is weak at static loads (effective front grip 1.83 for the Corolla against 1.81 for the RX-7) and only grows if the load per wheel gets large;
  - the **front/rear balance** (understeer, mild oversteer), which depends mostly on how the weight is split between the axles.
- **About the RX-7:** with the same parts and unique packages its overall performance felt about equivalent. Its cornering behaviour (understeer/oversteer) only resembled the Corolla's with about 52 % of its weight on the rear axle instead of 41 %.

The Corolla's own figures: light (0.970 t), weight further back than almost any other car (46.0 % on the rear axle), and an effective front grip at the top of the field (1.828), by a margin well within the noise of a static model.

## The numbers (31 playable cars, 11 RWD)

Read from the car table, or computed from it (effective grip and stage 3 torque are my estimates, see `FIELDS.md`).

| | Corolla | RX-7 | RWD median | Corolla's rank |
|---|---|---|---|---|
| Mass | 0.970 t | 1.220 t | 1.45 t | 2nd lightest of 31 (Peugeot 106: 0.961 t), lightest RWD |
| Weight on rear axle | 46.0 % | 41.4 % | 42.4 % | 3rd of 31 (Escalade 47.5 %, 240SX 46.9 %), 2nd of 11 RWD |
| Front friction-circle mu, stock | 1.425 | 1.70 | 1.67 | lowest of 31 |
| Front friction-circle mu, stage 3 | 1.85 | 1.90 | | |
| Effective front grip, stage 3 (estimate) | 1.828 | 1.813 | | 1st of 31 by about 0.8 % (240SX 1.817, Civic 1.815, Miata 1.815, RX-7 5th): within the noise of a static model without load transfer; about 20 cars within 1.80-1.83 |
| Peak torque, stock | 130 N.m | 190 N.m | 285 N.m | lowest of 31 |
| Torque per tonne, stage 3 (estimate, turbo table only) | 278 | 277 | 278 | median |

At max parts the Corolla is average to high, not beyond its peers in power or grip (estimates). What stands out is the shape of the car: light, with its weight further back.

## The closest car on two criteria (rear weight and front grip): the 240SX

The 240SX is the car most similar in rear-weight share and front grip. It is also a quarter heavier with stiffer stage 3 springs.

| | Corolla | 240SX | RX-7 |
|---|---|---|---|
| Weight on rear axle | 46.0 % | 46.9 % | 41.4 % |
| CoG offset x | 0.245 | 0.245 | 0.225 |
| Wheelbase | 2.40 m | 2.44 m | 2.45 m |
| Effective front grip, stage 3 | 1.828 | 1.817 | 1.813 |
| Effective rear grip, stage 3 | 1.830 | 1.823 | 1.830 |
| Torque per tonne, stage 3 (estimate) | 278 | 289 | 277 |
| Mass | 0.970 t | 1.220 t | 1.220 t |
| Load per front wheel | 2.56 kN | 3.17 kN | 3.50 kN |
| Tyre radius | 0.265 m | 0.314 m | 0.316 m |
| Front half-track | 0.678 m | 0.730 m | 0.730 m |
| Stage 3 springs, front / rear | 50 / 50 | 75 / 70 | 69 / 60 |
| Wheel hardpoint height vs CoG | +0.025 | -0.160 | -0.120 |

Sensitivity illustration of the static model, with downforce added as a fraction f of the weight (the real f is unknown, see the next section):

| f | Front/rear grip, Corolla / 240SX / RX-7 | Lateral g, Corolla / 240SX / RX-7 |
|---|---|---|
| 1.0 | 0.992 / 0.977 / 0.936 | 1.79 / 1.72 / 1.69 |
| 2.0 | 0.967 / 0.954 / 0.862 | 1.65 / 1.52 / 1.44 |

In this illustration the 240SX sits between the other two: close to the Corolla in front/rear balance, nearer to the RX-7 in absolute lateral grip (it carries about 24 % more load per wheel). It is close on rear weight and front grip, not overall: on a broad 13-parameter distance across all 31 cars (an arbitrary choice of parameters), the 240SX is only the 9th-nearest car to the Corolla and the RX-7 the 3rd. I have not driven the 240SX in game for this.

## Model illustration: sensitivity to aero load (not an explanation)

1. The aero term exists. The PC executable's per-wheel load function adds an aero term to the weight; its coefficient is 0 for the Corolla in stock. How large the term is, and whether it depends on speed (and how), is not verified. The real ratio f of added downforce to weight is therefore unknown.
2. The tyre's lateral-force curve (reconstructed from the PS2 build's documentation) is concave: past about 5 kN per wheel, each extra kN of load adds less grip.
3. What the static model shows is its own sensitivity: if the added load were large enough to push the most heavily loaded axle past that point, that axle would lose grip first. The RX-7 (58.6 % of its weight on the front, 3.5 kN per front wheel) would be affected before the Corolla (54 %, 2.56 kN). The sweep over f = 0, 1 and 2 is in [`FIELDS.md`](FIELDS.md). f = 2 (downforce twice the car's weight) is probably unrealistic, and no value of f is established. This illustrates what the model would do; it does not explain the behaviour observed in game.

## In-game tests (one tester, subjective feel)

All experiments are in `nfsu2_statcard_patch.py` and were applied to a real install, with both cars at maximum parts, in corners at roughly 180 km/h.

| Test | Result |
|---|---|
| RX-7 given the Corolla's parts and unique packages (save edit) | overall performance felt roughly equivalent |
| `control`: Corolla 30 % / RX-7 58 % rear weight | clear change; RX-7 oversteers more than the stock Corolla. The edit is applied even with max parts |
| `swap`: the two cars swap their rear-weight shares | small change |
| `rx7-52`: RX-7 at 52 % rear weight | RX-7 corners like the Corolla |
| `wheel-z`: Corolla wheel hardpoint height to the RWD median | no noticeable change |
| `cog-z`: Corolla CoG height, hardpoint gap to the RWD median | no noticeable change |

The weight distribution is a real lever: `control` moved the behaviour a lot, `rx7-52` brought the RX-7 to the Corolla's cornering, and `swap` changed it only a little. The weak effect of `swap` is consistent with this: the gap between the two shares is small (46 % against 41 %, about five points), much less than the 52 % that was needed, and far less than the shifts of `control` (30 % and 58 %).

The RX-7 needs about 52 % to imitate a Corolla that sits at 46 %, so something else also differs between the two cars. The total mass (load per wheel) is a candidate; it was not isolated.

## Not supported by the data or the tests

- **Higher raw grip:** at stage 3 the effective grip is 1.83 against 1.81 for the RX-7, which is within the noise of the model.
- **Too much torque on the rear wheels:** torque per tonne at stage 3 (estimate) is the median.
- **Smaller wheels preserving speed:** by my estimate the Corolla's shorter final drive (3.484 against 4.1) cancels the smaller radius; wheel force per kg comes out about equal.
- **A bug in the upgrade tables:** none found; the tables are regular, and the Corolla's start low.
- **Wheel and CoG height:** tested, no noticeable effect (subjective).

## Not established

- **The isolated effect of the total mass** was not tested in game. No test changes the Corolla's mass on its own.
- **The magnitude of the aero effect** at a given speed: two factors in the executable are unidentified, and whether and how the term depends on speed is not verified. The real downforce-to-weight ratio is unknown.
- **How much each remaining factor contributes** beyond the weight distribution.
- **Damping ratio:** the Corolla's front axle has the highest damping relative to mass (0.89 stock, 1.04 at stage 3, in assumed units). I do not think it explains the handling and did not test it.
- **The tests are subjective:** one tester, no instrumented timing. The model is a static estimate rebuilt from the PS2 build's documentation, checked on the PC data where possible.

Suggested protocol for the next step:

- **Blind test:** someone else applies a preset (or none) without telling the tester which one; the tester drives a few timed laps through the same corner and writes down a guess before the reveal. Compare lap times and guesses.
- **Mass on its own:** add a preset that changes the Corolla's mass (and inertia together) and nothing else, and run the same blind procedure. That would settle whether the mass matters beyond the weight distribution. Such a preset does not exist yet.

Please try it and report.

## Method in one paragraph

`GlobalB.lzc` is JDLZ-compressed; its decompressed content equals `GLOBALB.BUN` for the car table. The car table is a chunk of 46 fixed-size records. Field meanings come from the PS2 documentation, cross-checked on the PC data (wheelbase, mass, inertia formula, drivetrain pattern) and in `SPEED2.EXE`. Per-car comparisons are then plain statistics over the 31 playable cars. Each experiment edits a few floats and I checked that the patched files decode with a replica of the game's own decoder loop before they were tried in game.

References: see the README.
