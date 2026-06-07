"""
LUT lookup utilities for gm/Id characterization data — GF180MCU-D PDK.

Processed LUT files live under:
    asset_gf180mcuD/{device}/{corner}/{temp}/processed/gmid_{device}_L{l_nm}n.txt

Each .txt file is space-separated with ``#``-prefixed comment headers and
eleven data columns:

    gm/id [1/V]  gm/gds [V/V]  id/W [A/m]  ft [Hz]
    Cgg/W [F/m]  Cgd/W [F/m]  Cgs/W [F/m]  Cdb/W [F/m]
    vgs [V]      vth [V]      vdsat [V]

The DataFrame returned by :func:`load_lut` uses these clean column names:

    gm_id  gm_gds  id_w  ft  cgg_w  cgd_w  cgs_w  cdb_w  vgs  vth  vdsat

Unit notes (backward-compatible with bridge code):
    * id_w  – stored A/m, numerically identical to µA/µm (1 A/m = 1 µA/µm)
    * cgg_w, cgd_w, cgs_w, cdb_w – stored F/m, kept as-is
    * ft    – stored Hz, kept as-is
    * gm_gds – stored directly (no inversion needed)
    * vgs, vth, vdsat – V (vth and vdsat are positive magnitudes for both
      polarities; ngspice convention)

`vdsat` is the BSIM4 internal saturation voltage (|VDS|_sat including
velocity-saturation / short-channel effects). It is the canonical quantity
for all headroom, saturation-margin, and cascode-bias calculations. The
LUT does not carry a square-law overdrive column — `vdsat`, `vth`, and
`vgs` are the only voltage axes exposed.

Filename convention:
    gmid_{device}_L{l_nm}n.txt   e.g. gmid_nfet_03v3_L280n.txt

Device naming:
    Accepts 'nfet', 'pfet', 'nfet_03v3', 'pfet_03v3'.
    Short forms are mapped to their full PDK names automatically.

Available reference temperatures (per GF180MCU-D characterization):
    -40C, 25C, 85C  per corner (5 corners: typical, ff, ss, fs, sf).
First-order linear interpolation between bracketing reference temperatures
is performed automatically by load_lut() for any in-range target temp.

PDK: GF180MCU-D
  Supply: 3.3 V
  Devices: nfet_03v3 (Lmin = 0.28 µm), pfet_03v3 (Lmin = 0.28 µm)
  Corners: typical, ff, ss, fs, sf
  Extrinsic cap source: sm141064.ngspice model card, typical corner, bin 0
"""

import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache
from typing import List, Optional, Union

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

ASSETS_DIR = Path(__file__).parent.parent / "asset_gf180mcuD"

# Short-name → full PDK folder name
_DEVICE_MAP = {
    "nfet": "nfet_03v3",
    "pfet": "pfet_03v3",
    "nfet_03v3": "nfet_03v3",
    "pfet_03v3": "pfet_03v3",
}

# ---------------------------------------------------------------------------
# GF180MCU-D extrinsic (layout-dependent) capacitance parameters
# ---------------------------------------------------------------------------
# These are NOT in the gm/ID LUT — they come from the BSIM4 model card
# and describe physical overlap and junction parasitics that the LUT's
# intrinsic cgs_w / cgd_w / cdb_w do not capture.
#
# Source: sm141064.ngspice, typical corner, bin 0 (Lmin = 0.28 µm)
#   - nfet_03v3.0 model  (lines 773–1015)
#   - pfet_03v3.0 model  (lines 19025–19270)
#
# The LUT cgd_w is the intrinsic channel-charge partition to the drain,
# which is ≈ 0 in saturation. The physical gate-drain overlap (cgdo × W)
# dominates and is typically 10–80× larger.

GF180_EXTRINSIC = {
    "nfet_03v3": {
        "cgdo":   1.0e-10,      # F/m — gate-drain overlap per unit width
        "cgso":   1.0e-10,      # F/m — gate-source overlap per unit width
        "cjs":    9.6797e-04,   # F/m² — drain junction area cap (zero-bias)
        "cjsws":  1.5663e-10,   # F/m — drain junction sidewall cap
        "cjswgs": 5.9903e-10,   # F/m — drain gate-edge sidewall cap per width
        "pbs":    0.70172,      # V — junction built-in potential
    },
    "pfet_03v3": {
        "cgdo":   1.24e-10,     # F/m — gate-drain overlap per unit width
        "cgso":   1.24e-10,     # F/m — gate-source overlap per unit width
        "cjs":    9.4344e-04,   # F/m² — drain junction area cap (zero-bias)
        "cjsws":  1.5078e-10,   # F/m — drain junction sidewall cap
        "cjswgs": 4.794e-10,    # F/m — drain gate-edge sidewall cap per width
        "pbs":    0.69939,      # V — junction built-in potential
    },
}

# Default diffusion extension beyond gate (m) — used for drain area/perimeter
# estimation when layout details are unavailable.
# GF180MCU-D 3.3V process: typical contacted diffusion extension ≈ 0.30 µm
_DIFF_EXT_M = 0.30e-6  # 0.30 µm

# Raw file column order → clean Python names (matches processed LUT header:
# gm/id  gm/gds  id/W  ft  Cgg/W  Cgd/W  Cgs/W  Cdb/W  vgs  vth  vdsat)
_RAW_COLUMNS = ["gm_id", "gm_gds", "id_w", "ft",
                "cgg_w", "cgd_w", "cgs_w", "cdb_w",
                "vgs",   "vth",   "vdsat"]

# Metrics that lut_query supports
_VALID_METRICS = set(_RAW_COLUMNS)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_device(device: str) -> str:
    """Map any accepted device alias to the canonical folder name."""
    canonical = _DEVICE_MAP.get(device)
    if canonical is None:
        raise KeyError(
            f"Unknown device '{device}'. "
            f"Accepted names: {sorted(_DEVICE_MAP.keys())}"
        )
    return canonical


def _lut_dir(device: str, corner: str, temp) -> Path:
    """Return the processed-LUT directory for a device/corner/temp combo."""
    return ASSETS_DIR / device / corner / str(temp) / "processed"


# ---------------------------------------------------------------------------
# Core I/O
# ---------------------------------------------------------------------------

def _parse_temp(temp) -> int:
    """Extract numeric temperature from a string like '25C' or '75C', or an int/float."""
    if isinstance(temp, (int, float)):
        return int(temp)
    return int(str(temp).rstrip("Cc"))


def _discover_temps(device: str, corner: str) -> List[int]:
    """Return sorted list of available reference temperatures (°C) for a device/corner."""
    corner_dir = ASSETS_DIR / device / corner
    if not corner_dir.exists():
        return []
    temps = []
    for d in corner_dir.iterdir():
        if d.is_dir() and (d / "processed").exists():
            try:
                temps.append(_parse_temp(d.name))
            except ValueError:
                continue
    temps.sort()
    return temps


def _load_processed_file(fpath: Path) -> pd.DataFrame:
    """Read a single processed LUT file into a DataFrame."""
    return pd.read_csv(
        fpath,
        sep=r"\s+",
        comment="#",
        header=None,
        names=_RAW_COLUMNS,
    )


def _trim_to_strong_inversion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop the sub-threshold branch so gm_id is monotonic across the table.

    Raw processed LUTs sweep VGS across the full range. gm/Id is not
    monotonic in VGS: it rises from a low value in strong inversion
    toward a peak (~25–30 S/A) at the onset of weak inversion, then
    falls again as the device enters deep sub-threshold. The two sides
    of the peak are therefore two physical branches sharing the same
    gm/Id axis.

    This function locates the peak and returns only the strong-inversion
    branch (the side with larger Id/W at its far end).
    """
    if df.empty or "gm_id" not in df.columns or "id_w" not in df.columns:
        return df

    peak_idx = int(df["gm_id"].idxmax())
    if peak_idx == 0 or peak_idx == len(df) - 1:
        return df.reset_index(drop=True)

    left  = df.iloc[: peak_idx + 1]
    right = df.iloc[peak_idx:]

    left_far_idw  = abs(left["id_w"].iloc[0])
    right_far_idw = abs(right["id_w"].iloc[-1])

    chosen = right if right_far_idw >= left_far_idw else left
    return chosen.reset_index(drop=True)


def _interpolate_lut(
    device: str,
    l_nm: int,
    corner: str,
    target_c: int,
    t_lo: int,
    t_hi: int,
) -> pd.DataFrame:
    """
    Linearly interpolate a processed LUT between two reference temperatures.

    Returns a DataFrame with the same columns as a regular processed LUT.
    """
    alpha = (target_c - t_lo) / (t_hi - t_lo)

    dir_lo = _lut_dir(device, corner, f"{t_lo}C")
    dir_hi = _lut_dir(device, corner, f"{t_hi}C")
    fname = f"gmid_{device}_L{l_nm}n.txt"

    f_lo = dir_lo / fname
    f_hi = dir_hi / fname

    if not f_lo.exists():
        raise FileNotFoundError(
            f"Reference LUT not found for interpolation: {f_lo}"
        )
    if not f_hi.exists():
        raise FileNotFoundError(
            f"Reference LUT not found for interpolation: {f_hi}"
        )

    df_lo = _load_processed_file(f_lo)
    df_hi = _load_processed_file(f_hi)

    df_lo = _trim_to_strong_inversion(df_lo)
    df_hi = _trim_to_strong_inversion(df_hi)

    n = min(len(df_lo), len(df_hi))
    df_lo = df_lo.iloc[:n].reset_index(drop=True)
    df_hi = df_hi.iloc[:n].reset_index(drop=True)

    df_interp = df_lo * (1 - alpha) + df_hi * alpha

    return df_interp


@lru_cache(maxsize=128)
def load_lut(
    device: str,
    l_nm: int,
    corner: str = "typical",
    temp: str = "25C",
) -> pd.DataFrame:
    """
    Load a gm/Id LUT for a given device, channel length, corner, and temp.

    If the exact temperature is not available on disk, automatically performs
    first-order linear interpolation between the two nearest bracketing
    reference temperatures.

    Args:
        device:  Device name — 'nfet', 'pfet', 'nfet_03v3', or 'pfet_03v3'.
        l_nm:    Channel length in nanometers (integer, e.g. 280).
        corner:  Process corner — 'typical', 'ff', 'ss', 'fs', 'sf'.
        temp:    Temperature string — '-40C', '25C', '85C' (reference
                 temps). Other in-range values are linearly interpolated.

    Returns:
        DataFrame with columns:
            gm_id, gm_gds, id_w, ft, cgg_w, cgd_w, cgs_w, cdb_w,
            vgs, vth, vdsat
    """
    canonical = _resolve_device(device)
    directory = _lut_dir(canonical, corner, temp)
    fname = directory / f"gmid_{canonical}_L{l_nm}n.txt"

    if fname.exists():
        df = pd.read_csv(
            fname,
            sep=r"\s+",
            comment="#",
            header=None,
            names=_RAW_COLUMNS,
        )
        return _trim_to_strong_inversion(df)

    # --- Auto-interpolation fallback ---
    target_c = _parse_temp(temp)
    available = _discover_temps(canonical, corner)

    if not available:
        raise FileNotFoundError(
            f"No reference temperatures found for device={device}, corner={corner}"
        )

    below = [t for t in available if t <= target_c]
    above = [t for t in available if t >= target_c]

    if not below or not above:
        raise FileNotFoundError(
            f"Cannot interpolate: target {target_c}°C is outside the available "
            f"range {available} for device={device}, corner={corner}. "
            f"Extrapolation is not supported."
        )

    t_lo = max(below)
    t_hi = min(above)

    if t_lo == t_hi:
        raise FileNotFoundError(
            f"LUT not found: {fname}\n"
            f"  device={device} ({canonical}), L={l_nm} nm, "
            f"corner={corner}, temp={temp}"
        )

    return _interpolate_lut(canonical, l_nm, corner, target_c, t_lo, t_hi)


# ---------------------------------------------------------------------------
# Main query API
# ---------------------------------------------------------------------------

def lut_query(
    device: str,
    metric: str,
    L: float,
    corner: str = "typical",
    temp: str = "25C",
    gm_id_val: Optional[float] = None,
) -> Union[pd.DataFrame, float]:
    """
    Unified LUT query — the primary API for bridge / skill code.

    Args:
        device:     'nfet', 'pfet', 'nfet_03v3', or 'pfet_03v3'.
        metric:     Column to retrieve.  One of:
                        gm_id, gm_gds, id_w, ft,
                        cgg_w, cgd_w, cgs_w, cdb_w,
                        vgs, vth, vdsat
        L:          Channel length in **micrometers** (e.g. 0.28 for 280 nm).
                    Converted to nm internally for the filename lookup.
        corner:     Process corner (default 'typical').
        temp:       Temperature string (default '25C').
        gm_id_val:  If given, linearly interpolate at this gm/Id point and
                    return a single float.  If None, return the full 2-column
                    DataFrame [gm_id, <metric>].

    Returns:
        pd.DataFrame  when gm_id_val is None (columns: gm_id, metric).
        float         when gm_id_val is provided.

    Raises:
        FileNotFoundError: LUT file does not exist.
        ValueError:        gm_id_val outside the table range.
        KeyError:          Unrecognised device or metric.
    """
    if metric not in _VALID_METRICS:
        raise KeyError(
            f"Unknown metric '{metric}'. Valid metrics: {sorted(_VALID_METRICS)}"
        )

    l_nm = int(round(L * 1000))
    df = load_lut(device, l_nm, corner=corner, temp=temp)

    series = df[metric]

    if gm_id_val is not None:
        lo, hi = df["gm_id"].min(), df["gm_id"].max()
        if not (lo <= gm_id_val <= hi):
            raise ValueError(
                f"gm_id_val={gm_id_val} is outside LUT range "
                f"[{lo:.4f}, {hi:.4f}] for device={device}, L={L} µm, "
                f"corner={corner}, temp={temp}."
            )
        sort_idx = np.argsort(df["gm_id"].values)
        return float(
            np.interp(
                gm_id_val,
                df["gm_id"].values[sort_idx],
                series.values[sort_idx],
            )
        )

    return pd.DataFrame({"gm_id": df["gm_id"].values, metric: series.values})


# ---------------------------------------------------------------------------
# Discovery helpers
# ---------------------------------------------------------------------------

def list_available_L(
    device: str,
    corner: str = "typical",
    temp: str = "25C",
) -> List[float]:
    """
    Return sorted list of available channel lengths (in µm) for a device.

    Scans the processed LUT directory for matching filenames and extracts
    the L value from each.

    Args:
        device:  Device name (any accepted alias).
        corner:  Process corner (default 'typical').
        temp:    Temperature string (default '25C').

    Returns:
        Sorted list of L values in micrometers (e.g. [0.28, 0.56, ...]).
    """
    canonical = _resolve_device(device)
    directory = _lut_dir(canonical, corner, temp)

    if not directory.exists():
        target_c = _parse_temp(temp)
        available = _discover_temps(canonical, corner)
        if not available:
            raise FileNotFoundError(
                f"LUT directory not found: {directory}\n"
                f"  device={device} ({canonical}), corner={corner}, temp={temp}"
            )
        ref_temp = min(available, key=lambda t: abs(t - target_c))
        directory = _lut_dir(canonical, corner, f"{ref_temp}C")

    lengths_nm: List[int] = []
    prefix = f"gmid_{canonical}_L"
    for f in directory.iterdir():
        name = f.name
        if name.startswith(prefix) and name.endswith("n.txt"):
            num_str = name[len(prefix):-len("n.txt")]
            try:
                lengths_nm.append(int(num_str))
            except ValueError:
                continue

    lengths_nm.sort()
    return [l / 1000.0 for l in lengths_nm]


# ---------------------------------------------------------------------------
# Convenience wrappers (backward-compatible)
# ---------------------------------------------------------------------------

def lookup_by_gmid(
    device: str,
    l_nm: int,
    gm_id: float,
    col: str,
    corner: str = "typical",
    temp: str = "25C",
) -> float:
    """
    Look up a LUT column value at a specific gm/Id by linear interpolation.

    Args:
        device:  Device name (any accepted alias, e.g. 'nfet', 'nfet_03v3').
        l_nm:    Channel length in nm.
        gm_id:   Target gm/Id ratio (1/V).
        col:     Column name — one of the clean names.
        corner:  Process corner (default 'typical').
        temp:    Temperature (default '25C').
    """
    df = load_lut(device, l_nm, corner=corner, temp=temp)
    if col not in df.columns:
        raise KeyError(
            f"Column '{col}' not in LUT. Available: {list(df.columns)}"
        )
    sort_idx = np.argsort(df["gm_id"].values)
    return float(
        np.interp(gm_id, df["gm_id"].values[sort_idx], df[col].values[sort_idx])
    )


def lookup_gm_gds(
    device: str, l_nm: int, gm_id: float,
    corner: str = "typical", temp: str = "25C",
) -> float:
    """Return intrinsic gain gm/gds (V/V) for a given gm/Id and L."""
    return lookup_by_gmid(device, l_nm, gm_id, "gm_gds", corner=corner, temp=temp)


def lookup_id_w(
    device: str, l_nm: int, gm_id: float,
    corner: str = "typical", temp: str = "25C",
) -> float:
    """Return Id/W (A/m ≡ µA/µm) for a given gm/Id and L."""
    return lookup_by_gmid(device, l_nm, gm_id, "id_w", corner=corner, temp=temp)


def lookup_cgg_w(
    device: str, l_nm: int, gm_id: float,
    corner: str = "typical", temp: str = "25C",
) -> float:
    """Return Cgg/W (F/m) for a given gm/Id and L."""
    return lookup_by_gmid(device, l_nm, gm_id, "cgg_w", corner=corner, temp=temp)


def lookup_ft(
    device: str, l_nm: int, gm_id: float,
    corner: str = "typical", temp: str = "25C",
) -> float:
    """Return fT (Hz) for a given gm/Id and L."""
    return lookup_by_gmid(device, l_nm, gm_id, "ft", corner=corner, temp=temp)


# ---------------------------------------------------------------------------
# Extrinsic capacitance helpers
# ---------------------------------------------------------------------------

def extrinsic_caps(
    device: str,
    W_m: float,
    M: int = 1,
) -> dict:
    """
    Compute extrinsic (overlap + junction) capacitances not in the gm/ID LUT.

    The LUT stores *intrinsic* small-signal caps (channel charge partition).
    This function returns the *extrinsic* components from the BSIM4 model card:
      - Cgd_overlap: gate-drain overlap (cgdo × W_total)
      - Cgs_overlap: gate-source overlap (cgso × W_total)
      - Cdb_perim:   drain junction perimeter + gate-edge sidewall cap

    The returned values should be ADDED to the LUT-derived intrinsic caps.

    Args:
        device:  'nfet' or 'pfet' (or full PDK name 'nfet_03v3' / 'pfet_03v3').
        W_m:     Total device width in meters (all instances combined).
        M:       Multiplier (number of parallel instances). Used to
                 estimate drain perimeter.

    Returns:
        dict with keys:
            'cgd_ov':  gate-drain overlap cap (F)
            'cgs_ov':  gate-source overlap cap (F)
            'cdb_sw':  drain junction sidewall + gate-edge cap (F)
    """
    canonical = _resolve_device(device)
    ex = GF180_EXTRINSIC.get(canonical)
    if ex is None:
        return {"cgd_ov": 0.0, "cgs_ov": 0.0, "cdb_sw": 0.0}

    W_total = W_m

    cgd_ov = ex["cgdo"] * W_total
    cgs_ov = ex["cgso"] * W_total

    n_drains = max(1, (M + 1) // 2)  # shared-drain interdigitated assumption
    W_inst = W_total / max(M, 1)
    P_drain = n_drains * 2 * (W_inst + _DIFF_EXT_M)

    cdb_sw = ex["cjsws"] * P_drain + ex["cjswgs"] * W_total

    return {
        "cgd_ov": cgd_ov,
        "cgs_ov": cgs_ov,
        "cdb_sw": cdb_sw,
    }


def pdk_cdb(
    device: str,
    W_m: float,
    M: int = 1,
) -> float:
    """
    Compute total drain-bulk junction cap from PDK parameters (first-principles).

    Use this INSTEAD of (cdb_w × W + extrinsic cdb_sw) when accurate Cdb
    is needed.

        Cdb = cjs × A_drain + cjsws × P_drain + cjswgs × W_total

    Args:
        device:  'nfet' or 'pfet' (or full PDK name).
        W_m:     Total device width in meters.
        M:       Multiplier (number of parallel instances).

    Returns:
        Total drain-bulk junction capacitance in Farads (zero-bias).
    """
    canonical = _resolve_device(device)
    ex = GF180_EXTRINSIC.get(canonical)
    if ex is None:
        return 0.0

    W_total = W_m
    W_inst = W_total / max(M, 1)
    n_drains = max(1, (M + 1) // 2)

    A_drain = n_drains * W_inst * _DIFF_EXT_M
    P_drain = n_drains * 2 * (W_inst + _DIFF_EXT_M)

    return (ex["cjs"] * A_drain
            + ex["cjsws"] * P_drain
            + ex["cjswgs"] * W_total)
