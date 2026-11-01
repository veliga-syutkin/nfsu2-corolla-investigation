#!/usr/bin/env python3
"""nfsu2_statcard_patch.py - reproducible stat-card experiments for NFS Underground 2 (PC).

Applies a handful of byte changes to YOUR OWN copy of GLOBAL/GLOBALB.BUN and GLOBAL/GlobalB.lzc.
No game data is included here. Always keep the original files (the `install` command does it for you).

Commands:
  list                      show the available experiments
  inspect  --game GLOBAL    print the Corolla / RX7 stat-card values read from your files
  build    PRESET --game GLOBAL --out DIR     write patched copies to DIR (game folder untouched)
  install  PRESET --game GLOBAL               back up originals, then install the patched files
  restore  --game GLOBAL                      put the original files back

Python 3, standard library only. See README.md and docs/ for what each value means and the references.
"""
import argparse
import os
import shutil
import struct
import sys

REC = 2192            # size of one car record
CARS_CHUNK = 0x34600  # chunk id of the car table in GLOBALB
NAME = 8              # car name inside a record
COG = 0x118           # centre-of-gravity offset (x, y, z) from the model origin
WHEEL = 0x128         # wheel 0 (x, y, z, ...); wheels are 0x30 apart, 0 and 1 = front
MASS = 0x228          # mass in tonnes


def rf(b, o):
    return struct.unpack_from('<f', b, o)[0]


def wf(b, o, v):
    struct.pack_into('<f', b, o, v)


# ---------------------------------------------------------------- JDLZ (GlobalB.lzc)
# Format reference: Luigi Auriemma, ea_jdlz.c (http://aluigi.altervista.org/papers/ea_jdlz.c);
# behaviour checked against the decoder loop in SPEED2.EXE (0x573710).
def jdlz_decode(data):
    if data[:4] != b'JDLZ':
        raise SystemExit('not a JDLZ file')
    outsz = struct.unpack_from('<I', data, 8)[0]
    out = bytearray(outsz)
    ip, o, f1, f2 = 16, 0, 1, 1
    while ip < len(data) and o < outsz:
        if f1 == 1:
            f1 = data[ip] | 0x100
            ip += 1
        if f2 == 1:
            f2 = data[ip] | 0x100
            ip += 1
        if f1 & 1:
            if f2 & 1:
                length = (data[ip + 1] | ((data[ip] & 0xF0) << 4)) + 3
                t = (data[ip] & 0xF) + 1
            else:
                t = (data[ip + 1] | ((data[ip] & 0xE0) << 3)) + 17
                length = (data[ip] & 0x1F) + 3
            ip += 2
            for i in range(length):
                if o + i >= outsz:
                    break
                out[o + i] = out[o + i - t]
            o += min(length, outsz - o)
            f2 >>= 1
        else:
            out[o] = data[ip]
            o += 1
            ip += 1
        f1 >>= 1
    return bytes(out)


def jdlz_encode_literal(data):
    """Valid JDLZ stream with no back-references (bigger file, trivially correct).
    The game's loop ends when a byte counter hits exactly 0 and re-reads a control byte after every
    complete group of 8 items, so a final control byte is required when len(data) % 8 == 0."""
    n = len(data)
    body = bytearray([0, 0])
    i = 0
    while i < n:
        body += data[i:i + 8]
        i += 8
        if i % 8 == 0 and (i < n or n % 8 == 0):
            body.append(0)
    return b'JDLZ' + bytes([2, 0x10, 0, 0]) + struct.pack('<II', n, 16 + len(body)) + bytes(body)


# ---------------------------------------------------------------- stat card access
def records(buf):
    pos = 0
    while pos + 8 <= len(buf):
        cid, size = struct.unpack_from('<II', buf, pos)
        if cid == CARS_CHUNK:
            body, out = pos + 8, {}
            for i in range(size // REC):
                o = body + i * REC
                out[bytes(buf[o + NAME:o + NAME + 32]).split(b'\0')[0].decode('ascii', 'replace')] = o
            return out
        pos += 8 + size
    raise SystemExit('car table (chunk 0x34600) not found: not a NFSU2 PC GLOBALB file?')


def rear_share(buf, o):
    xf, xr = rf(buf, o + WHEEL), rf(buf, o + WHEEL + 0x30 * 3)
    return (xf - rf(buf, o + COG)) / (xf - xr)


def set_rear_share(buf, o, share):
    xf, xr = rf(buf, o + WHEEL), rf(buf, o + WHEEL + 0x30 * 3)
    wf(buf, o + COG, xf - share * (xf - xr))


def need(buf, recs, *names):
    for n in names:
        if n not in recs:
            raise SystemExit('car %s not found in this file' % n)


# ---------------------------------------------------------------- experiments
def p_rx7_52(buf, recs):
    need(buf, recs, 'RX7')
    set_rear_share(buf, recs['RX7'], 0.52)


def p_control(buf, recs):
    need(buf, recs, 'COROLLA', 'RX7')
    set_rear_share(buf, recs['COROLLA'], 0.30)
    set_rear_share(buf, recs['RX7'], 0.58)


def p_swap(buf, recs):
    need(buf, recs, 'COROLLA', 'RX7')
    c, r = recs['COROLLA'], recs['RX7']
    sc, sr = rear_share(buf, c), rear_share(buf, r)
    set_rear_share(buf, c, sr)
    set_rear_share(buf, r, sc)


def p_wheel_z(buf, recs):
    need(buf, recs, 'COROLLA')
    o = recs['COROLLA']
    for w in range(4):
        a = o + WHEEL + 0x30 * w + 8
        if abs(rf(buf, a) - 0.275) > 1e-5:
            raise SystemExit('unexpected Corolla wheel height: %r (expected 0.275)' % rf(buf, a))
        wf(buf, a, 0.146)


def p_cog_z(buf, recs):
    need(buf, recs, 'COROLLA')
    a = recs['COROLLA'] + COG + 8
    if abs(rf(buf, a) - 0.25) > 1e-5:
        raise SystemExit('unexpected Corolla CoG height: %r (expected 0.25)' % rf(buf, a))
    wf(buf, a, 0.3823)


PRESETS = {
    'rx7-52': (p_rx7_52, 'RX7: 52 % of the weight on the rear axle (stock 41.4 %). One tester, subjective: RX7 corners like the Corolla.'),
    'control': (p_control, 'Positive control: Corolla 30 %, RX7 58 % rear weight. One tester, subjective: clear change (RX7 oversteers more than stock Corolla).'),
    'swap': (p_swap, 'Corolla and RX7 swap their rear-weight shares (46.0 % <-> 41.4 %). One tester, subjective: small change.'),
    'wheel-z': (p_wheel_z, 'Corolla wheel hardpoint height 0.275 -> 0.146 (RWD median). One tester, subjective: no noticeable change.'),
    'cog-z': (p_cog_z, 'Corolla CoG height 0.25 -> 0.3823 (hardpoint-to-CoG gap at the RWD median). One tester, subjective: no noticeable change.'),
}


# ---------------------------------------------------------------- file handling
def find_files(folder):
    found = {}
    for n in os.listdir(folder):
        if n.lower() in ('globalb.bun', 'globalb.lzc'):
            found[n] = os.path.join(folder, n)
    if not found:
        raise SystemExit('no GLOBALB.BUN / GlobalB.lzc in %s' % folder)
    return found


def load(path):
    raw = open(path, 'rb').read()
    return raw, (bytearray(jdlz_decode(raw)) if path.lower().endswith('.lzc') else bytearray(raw))


def patched(path, preset):
    raw, buf = load(path)
    before = bytes(buf)
    PRESETS[preset][0](buf, records(buf))
    changed = [i for i in range(len(buf)) if buf[i] != before[i]]
    out = jdlz_encode_literal(bytes(buf)) if path.lower().endswith('.lzc') else bytes(buf)
    return out, len(changed)


def backup_dir(game):
    return os.path.join(os.path.dirname(os.path.abspath(game)), 'GLOBAL_original_backup')


def cmd_inspect(a):
    path = sorted(find_files(a.game).values())[0]
    _, buf = load(path)
    recs = records(buf)
    print('read from', path)
    for n in ('COROLLA', 'RX7'):
        if n in recs:
            o = recs[n]
            print('%-8s mass %.3f t | CoG (%.3f, %.3f, %.3f) | rear weight share %.2f %% | front axle mu %.3f | rear axle mu %.3f'
                  % (n, rf(buf, o + MASS), rf(buf, o + COG), rf(buf, o + COG + 4), rf(buf, o + COG + 8),
                     100 * rear_share(buf, o), rf(buf, o + 0x1e8 + 12), rf(buf, o + 0x208 + 12)))


def cmd_build(a):
    os.makedirs(a.out, exist_ok=True)
    for name, path in find_files(a.game).items():
        data, n = patched(path, a.preset)
        open(os.path.join(a.out, name), 'wb').write(data)
        print('%s: %d value byte(s) changed -> %s' % (name, n, os.path.join(a.out, name)))


def cmd_install(a):
    bk = backup_dir(a.game)
    files = find_files(a.game)
    if not os.path.isdir(bk):
        os.makedirs(bk)
        for name, path in files.items():
            shutil.copy2(path, os.path.join(bk, name))
        print('originals backed up in', bk)
    else:
        print('backup already present (%s), kept untouched' % bk)
    for name, path in files.items():
        data, n = patched(os.path.join(bk, name), a.preset)   # always start from the originals
        open(path, 'wb').write(data)
        print('%s: %d value byte(s) changed, installed' % (name, n))
    print('Done. Run "restore" to go back.')


def cmd_restore(a):
    bk = backup_dir(a.game)
    if not os.path.isdir(bk):
        raise SystemExit('no backup folder: %s' % bk)
    for name in os.listdir(bk):
        shutil.copy2(os.path.join(bk, name), os.path.join(a.game, name))
        print('restored', name)


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    s = p.add_subparsers(dest='cmd', required=True)
    s.add_parser('list').set_defaults(fn=lambda a: [print('%-8s %s' % (k, v[1])) for k, v in PRESETS.items()])
    for c, fn in (('inspect', cmd_inspect), ('build', cmd_build), ('install', cmd_install), ('restore', cmd_restore)):
        q = s.add_parser(c)
        if c in ('build', 'install'):
            q.add_argument('preset', choices=sorted(PRESETS))
        q.add_argument('--game', required=True, help='the GLOBAL folder of your NFSU2 install')
        if c == 'build':
            q.add_argument('--out', required=True)
        q.set_defaults(fn=fn)
    a = p.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
