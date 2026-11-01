# nfsu2-corolla-investigation

Reproducible experiments behind a question the NFS Underground 2 community keeps asking: **why does the Corolla (AE86) feel so much better than the other RWD cars once it has maximum performance parts?** Is it a bug? Does it need a mod?

**Short answer:** nothing in the game's car table points to a bug, and no modding is needed to see the behaviour. The one lever demonstrated in game so far is the weight distribution between the axles. The total mass and the aero are plausible contributors that the tests did not isolate. This repository holds the small tool used to reproduce the experiments on a real install.

> **TL;DR (read from, or computed from, the game's own car table: 31 playable cars, max performance parts)**
> - **Light:** 0.970 t, second-lightest of 31 (Peugeot 106: 0.961 t) and the lightest of the 11 RWD cars (median 1.45 t).
> - **Weight further back than almost any other car:** 46.0 % of its weight sits on the rear axle. Only the Escalade (47.5 %) and the 240SX (46.9 %) are higher; the RWD median is 42.4 %. The RX-7 is at 41.4 %.
> - **Effective front grip at the top of the field, within the noise:** 1.828 (min of the tyre curve at its static wheel load and the stage 3 friction circle; my estimate). #1 of 31, but only ~0.8 % ahead of the 240SX (1.817) and RX-7 (1.813), which is within the noise of a static model, and about twenty cars sit between 1.80 and 1.83.
> - **Demonstrated lever (in-game tests, one tester, subjective feel):** the weight distribution between the axles. With the same parts and unique packages the RX-7's overall performance felt about equivalent, but it only corners like the Corolla with 52 % of its weight on the rear axle.
> - **Plausible, not isolated by the tests:** total mass (load per wheel) and the aero. The aero term exists in the game's per-wheel load function, but its size and its dependence on speed are unknown.

*Fun fact: in stock the Corolla has the lowest grip and torque of all 31 cars. Max parts bring it to about the average (and to the top of the field for front grip, by a small margin), so don't expect a flagrant gap at stage 3 on paper.*

Details, tests and caveats: [`docs/FINDINGS.md`](docs/FINDINGS.md). What each value is and where it comes from: [`docs/FIELDS.md`](docs/FIELDS.md).
## What is (and is not) in this repository

**No game files are distributed here.** The experiments are a few changed bytes applied to *your own* copy of `GLOBAL/GLOBALB.BUN` and `GLOBAL/GlobalB.lzc` by a small Python script. They exist **only to reproduce the experiments** and to show that changing these car-table values changes the behaviour. They are not a gameplay mod, and modified game files must not be redistributed.

Not affiliated with Electronic Arts or any NFSU2 web port. You need your own legal copy of the game (PC, v1.2).

## Back up your originals first

Before anything else, copy `GLOBALB.BUN` and `GlobalB.lzc` somewhere safe. The `install` command also does this for you: it saves them in a `GLOBAL_original_backup` folder next to `GLOBAL` (and never overwrites an existing backup), and it always builds the patched files from those backups, so you can switch between experiments without stacking changes. `restore` puts the originals back. Close the game before installing.

## Usage

Requires Python 3 (standard library only). On Windows use `py` instead of `python3`.

```
python3 nfsu2_statcard_patch.py list
python3 nfsu2_statcard_patch.py inspect --game "<path>/Need for Speed Underground 2/GLOBAL"
python3 nfsu2_statcard_patch.py build   rx7-52 --game "<path>/GLOBAL" --out ./out   # writes copies, touches nothing
python3 nfsu2_statcard_patch.py install rx7-52 --game "<path>/GLOBAL"               # backup, then install
python3 nfsu2_statcard_patch.py restore        --game "<path>/GLOBAL"
```

The tool finds the Corolla and RX-7 records by name and refuses to patch a file whose values are not the expected ones. `GlobalB.lzc` is rewritten as an uncompressed JDLZ stream (about 9 MB instead of 5 MB), which the game accepts.

## The experiments

| Preset | What it changes | Result in game (one tester, subjective) |
|---|---|---|
| `rx7-52` | RX-7: 52 % of the weight on the rear axle (stock 41.4 %) | RX-7 corners like the Corolla |
| `control` | Corolla 30 % / RX-7 58 % rear weight (exaggerated) | clear change: RX-7 oversteers more than the stock Corolla; shows the edit is applied even with max parts |
| `swap` | Corolla and RX-7 swap their rear-weight shares | small change (the gap between 46 % and 41 % is small) |
| `wheel-z` | Corolla wheel hardpoint height set to the RWD median | no noticeable change |
| `cog-z` | Corolla centre-of-gravity height set so the hardpoint gap matches the RWD median | no noticeable change |

All five were checked byte for byte against the files that were tested in game. Test conditions: one tester, subjective feel, around 180 km/h corners, Wine on Linux, R.G. Mechanics repack of v1.2. A blind, timed protocol for the next step is proposed in [`docs/FINDINGS.md`](docs/FINDINGS.md).

## References

What this work builds on (thank you to the authors):

1. **nfsu2-native** (NFSU2 PS2 PAL functional decompilation and native port), by mad0xstrixhadorami: record layout, tyre model, performance-part categories. Files used: [`docs/physics.md`](https://github.com/mad0xstrixhadorami/nfsu2-native/blob/HEAD/docs/physics.md), [`src/game/indep/Frontend/PerfModel.h`](https://github.com/mad0xstrixhadorami/nfsu2-native/blob/HEAD/src/game/indep/Frontend/PerfModel.h), [`PerfPackages.h`](https://github.com/mad0xstrixhadorami/nfsu2-native/blob/HEAD/src/game/indep/Frontend/PerfPackages.h), [`src/game/indep/Physics/UG2Vehicle.cpp`](https://github.com/mad0xstrixhadorami/nfsu2-native/blob/HEAD/src/game/indep/Physics/UG2Vehicle.cpp). https://github.com/mad0xstrixhadorami/nfsu2-native
2. **`ea_jdlz.c`** by Luigi Auriemma, the reference for the JDLZ format of `GlobalB.lzc`: http://aluigi.altervista.org/papers/ea_jdlz.c
3. **nfsu2.xyz** ([th0mk/nfsu2-web](https://github.com/th0mk/nfsu2-web)): its public client code shows the car-name hash and how the game's own checks read the data.
4. **Own disassembly of `SPEED2.EXE` v1.2** (objdump), to check the above on the PC build: the JDLZ decoder loop (`0x573710`) and the per-wheel static load function (`0x598a00`).

The PS2 documents describe the PS2 build. Where I could, I verified the layout on the PC data; see the confidence column in [`docs/FIELDS.md`](docs/FIELDS.md).

## License

Code: MIT, see [LICENSE](LICENSE).
