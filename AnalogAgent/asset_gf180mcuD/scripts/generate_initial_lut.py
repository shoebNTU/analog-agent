#!/usr/bin/env python3
"""
Generate initial gm/ID LUT for GF180MCU-D nfet_03v3 and pfet_03v3.

Run this script INSIDE the iic-osic-tools Docker container (or set NGSPICE and
PDK_LIB environment variables to point to your local copies):

    docker exec -it <container_id_or_name> bash
    cd /foss/designs/share_GF180_Analog
    conda activate Agent
    python AnalogAgent/asset_gf180mcuD/scripts/generate_initial_lut.py

Sweep grid:
  - Devices : nfet_03v3, pfet_03v3
  - Corners : typical, ff, ss, fs, sf
  - Temps   : -40C, 25C, 85C
  - W       : 2 um (fixed)
  - |VDS|   : 1.65 V  (half of VDD = 3.3 V)
  - L list  : 280n, 500n, 1u, 1.5u, 2u, 2.5u, 3u, 3.5u, 4u, 4.5u, 5u, 5.5u, 6u
  - VGS step: 10 mV
  - Columns : vgs, vth, vdsat, gm, id, gds, cgg, cgs, cgd, cdb  (10 columns)

vdsat is read directly from the BSIM internal variable: the minimum |VDS|
for saturation, with velocity-saturation and short-channel effects baked in.

Output layout (hierarchical, under asset_gf180mcuD/):
  asset_gf180mcuD/<device>/<corner>/<tempC>/initial/gmid_<device>_L<nm>n.txt
"""
import subprocess
import time
from pathlib import Path
import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# ngspice is at /foss/tools/bin/ngspice inside the container; fall back to PATH
NGSPICE = os.environ.get("NGSPICE", "/foss/tools/bin/ngspice")

# GF180MCU-D PDK location in the iic-osic-tools container. Prefer PDK_LIB
# from the environment; otherwise auto-detect a mounted CIEL GF180 PDK.
_PDK_CANDIDATES = sorted(
    Path("/foss/pdks/ciel/gf180mcu/versions").glob(
        "*/gf180mcuD/libs.tech/ngspice/sm141064.ngspice"
    )
)
_PDK_DEFAULT = str(_PDK_CANDIDATES[-1]) if _PDK_CANDIDATES else (
    "/path/to/gf180mcuD/libs.tech/ngspice/sm141064.ngspice"
)
PDK_LIB = os.environ.get("PDK_LIB", _PDK_DEFAULT)

# Design.ngspice is in the same folder as PDK_LIB (MC switches etc.)
DESIGN_NGSPICE = str(Path(PDK_LIB).parent / "design.ngspice")

# Output root: AnalogAgent/asset_gf180mcuD/
ASSET_GF = Path(__file__).resolve().parents[1]   # asset_gf180mcuD/
WORK_DIR = Path("/tmp/lut_char_gf180")

DEVICES = {
    "nfet_03v3": {"model_inner": "0", "polarity": "n"},
    "pfet_03v3": {"model_inner": "0", "polarity": "p"},
}

# Corner names exactly as they appear in sm141064.ngspice .LIB sections
CORNERS = ["typical", "ff", "ss", "fs", "sf"]
TEMPS   = [-40, 25, 85]

# L grid: starts at Lmin = 0.28 um (280 nm) for GF180MCU-D nfet_03v3/pfet_03v3
L_VALUES_NM = [280, 500, 1000, 1500, 2000, 2500, 3000,
               3500, 4000, 4500, 5000, 5500, 6000]

VDD      = 3.3
VDS      = 1.65   # |VDS| = VDD/2 for saturation bias
W_UM     = 2.0
VGS_STEP = 0.01   # 10 mV

BATCH_SIZE = 13   # all 13 L values in one ngspice invocation


# ---------------------------------------------------------------------------
# SPICE deck generation
# ---------------------------------------------------------------------------

def generate_spice(device, model_inner, polarity, corner, temp, l_values, raw_dir):
    """
    Build a single-batch ngspice DC sweep deck for one (device, corner, temp).

    NMOS: VS = 0,   VD = +1.65,  VG swept 0 → +3.3
    PMOS: VS = VDD, VD = +1.65,  VG swept 0 → +3.3  (VGS: -3.3 → 0, VDS: -1.65)

    The subcircuit nfet_03v3 / pfet_03v3 wraps the BSIM model so the
    internal MOSFET instance is always named m0.
    OP access: @m.xm{i}.m{model_inner}[gm]  →  @m.xm1.m0[gm]
    """
    L = []
    L.append(f"* GF180MCU-D {device} gm/ID LUT  |  corner={corner}  T={temp}C")
    L.append(f".include {DESIGN_NGSPICE}")
    L.append(f".lib '{PDK_LIB}' {corner}")
    L.append(f".temp {temp}")
    L.append(f"VDD vdd 0 {VDD}")
    L.append(f"VG  vg  0 1.65")

    if polarity == "n":
        L.append(f"VD_bias vd 0 {VDS}")
        src_node, b_node = "0", "0"
        sweep_start, sweep_stop = 0.0, VDD
    else:  # pmos — source at VDD
        L.append(f"VD_bias vd 0 {VDD - VDS}")   # 1.65
        src_node, b_node = "vdd", "vdd"
        sweep_start, sweep_stop = 0.0, VDD

    L.append("")
    for i, l_nm in enumerate(l_values, start=1):
        l_um = l_nm / 1000.0
        L.append(f"XM{i} d{i} vg {src_node} {b_node} {device} W={W_UM}u L={l_um}u")
        L.append(f"VD{i} vd d{i} 0")

    L.append("")
    L.append(".option wnflag=1")
    L.append(".option savecurrents")
    L.append("")
    L.append(".control")
    L.append("save all")
    # Internal OP variables — inner MOSFET is m0 for GF180 subckt models
    for i in range(1, len(l_values) + 1):
        for p in ("gm", "vth", "vdsat", "gds", "cgg", "cgs", "cgd", "cdb"):
            L.append(f"save @m.xm{i}.m{model_inner}[{p}]")
    L.append("")
    L.append(f"dc VG {sweep_start:.4f} {sweep_stop:.4f} {VGS_STEP:.4f}")
    L.append("remzerovec")
    L.append("")
    for i, l_nm in enumerate(l_values, start=1):
        raw = raw_dir / f"{device}_{corner}_{temp}C_L{l_nm}n.raw"
        params = [
            f"@m.xm{i}.m{model_inner}[gm]",
            f"i(VD{i})",
            f"@m.xm{i}.m{model_inner}[vth]",
            f"@m.xm{i}.m{model_inner}[vdsat]",
            f"@m.xm{i}.m{model_inner}[gds]",
            f"@m.xm{i}.m{model_inner}[cgg]",
            f"@m.xm{i}.m{model_inner}[cgs]",
            f"@m.xm{i}.m{model_inner}[cgd]",
            f"@m.xm{i}.m{model_inner}[cdb]",
        ]
        L.append(f"wrdata {raw} {' '.join(params)}")
    L.append("")
    L.append("quit 0")
    L.append(".endc")
    L.append(".end")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# wrdata → formatted LUT
# ---------------------------------------------------------------------------

def convert_raw(raw_file, device, polarity, corner, temp, l_nm):
    """
    ngspice wrdata pairs each saved value with its x-axis, so 9 saved vars
    yield 18 columns per row:
       0=vg  1=gm   2=vg 3=id   4=vg 5=vth   6=vg 7=vdsat
       8=vg 9=gds  10=vg 11=cgg 12=vg 13=cgs 14=vg 15=cgd 16=vg 17=cdb
    """
    if not raw_file.exists():
        return None

    rows = []
    with open(raw_file) as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            try:
                v = list(map(float, s.split()))
            except ValueError:
                continue
            if len(v) < 18:
                continue
            vg    = v[0]
            gm    = v[1]
            id_   = v[3]
            vth   = v[5]
            vdsat = v[7]
            gds   = v[9]
            cgg   = v[11]
            cgs   = v[13]
            cgd   = v[15]
            cdb   = v[17]

            if polarity == "n":
                vgs = vg            # VS = 0
            else:
                vgs = vg - VDD      # VS = VDD → VGS = VG - VDD (negative)

            rows.append([vgs, vth, vdsat, gm, id_, gds, cgg, cgs, cgd, cdb])

    if not rows:
        return None

    out_dir = ASSET_GF / device / corner / f"{temp}C" / "initial"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"gmid_{device}_L{l_nm}n.txt"

    l_um = l_nm / 1000.0
    vds_str = f"{VDS:.2f}" if polarity == "n" else f"-{VDS:.2f}  (VSD = {VDS:.2f})"
    with open(out_file, "w") as fh:
        fh.write(f"# GF180MCU-D {device} gm/ID Lookup Table\n")
        fh.write(f"# Corner: {corner}\n")
        fh.write(f"# Temperature: {temp} C\n")
        fh.write(f"# W = {W_UM:.1f} um\n")
        fh.write(f"# L = {l_um:.4g} um ({l_nm} nm)\n")
        fh.write(f"# VDS = {vds_str} V\n")
        fh.write(f"# VGS step = {VGS_STEP*1000:.0f} mV\n")
        fh.write("# vdsat = BSIM internal saturation voltage |VDS|_sat "
                 "(positive magnitude; minimum |VDS| for saturation)\n")
        fh.write("# Columns: vgs [V]  vth [V]  vdsat [V]  gm [S]  id [A]  "
                 "gds [S]  cgg [F]  cgs [F]  cgd [F]  cdb [F]\n")
        hdr = "#" + "".join(lbl.rjust(16) for lbl in
                            ["vgs", "vth", "vdsat", "gm", "id", "gds",
                             "cgg", "cgs", "cgd", "cdb"])
        fh.write(hdr + "\n")
        for r in rows:
            fh.write("".join(f"{x:16.6e}" for x in r) + "\n")

    return len(rows)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    combos = [(d, c, t) for d in DEVICES for c in CORNERS for t in TEMPS]
    total = len(combos)

    for idx, (device, corner, temp) in enumerate(combos, start=1):
        info = DEVICES[device]
        print(f"\n[{idx}/{total}] {device} / {corner} / {temp}C", flush=True)

        raw_dir = WORK_DIR / device / corner / f"{temp}C"
        raw_dir.mkdir(parents=True, exist_ok=True)

        deck = generate_spice(device, info["model_inner"], info["polarity"],
                              corner, temp, L_VALUES_NM, raw_dir)
        deck_file = raw_dir / "deck.spice"
        deck_file.write_text(deck)

        t_start = time.time()
        try:
            res = subprocess.run(
                [NGSPICE, "-b", str(deck_file)],
                capture_output=True, text=True, timeout=600,
            )
        except subprocess.TimeoutExpired:
            print("  TIMEOUT"); continue
        dt = time.time() - t_start

        if res.returncode != 0:
            print(f"  ngspice FAILED (rc={res.returncode})  {dt:.1f}s")
            (raw_dir / "ngspice.log").write_text(res.stdout + "\n" + res.stderr)
            continue

        n_ok = 0
        for l_nm in L_VALUES_NM:
            raw = raw_dir / f"{device}_{corner}_{temp}C_L{l_nm}n.raw"
            n = convert_raw(raw, device, info["polarity"], corner, temp, l_nm)
            if n:
                n_ok += 1

        elapsed = time.time() - t0
        print(f"  OK  ngspice {dt:.1f}s  | {n_ok}/{len(L_VALUES_NM)} LUT files "
              f"| total elapsed {elapsed:.0f}s")

    print(f"\n{'='*60}")
    print(f"All done in {time.time()-t0:.0f}s → {ASSET_GF}/<device>/<corner>/<tempC>/initial/")


if __name__ == "__main__":
    main()
