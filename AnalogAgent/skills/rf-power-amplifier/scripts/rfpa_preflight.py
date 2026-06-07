#!/usr/bin/env python3
"""RF PA first-pass feasibility calculator.

This script is intentionally simple: it checks whether a requested output
power, load, pad frequency, and current limits are plausible before a design
flow starts sizing devices or matching networks.
"""

from __future__ import annotations

import argparse
import json
import math


ETA_GUESS = {
    "A": 0.35,
    "AB": 0.45,
    "B": 0.60,
    "C": 0.70,
    "E": 0.75,
    "F": 0.75,
}


def dbm_to_w(dbm: float) -> float:
    return 1e-3 * 10 ** (dbm / 10)


def w_to_dbm(watts: float) -> float:
    return 10 * math.log10(watts / 1e-3)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    pwr = parser.add_mutually_exclusive_group(required=True)
    pwr.add_argument("--pout-w", type=float, help="Target output power in W")
    pwr.add_argument("--pout-dbm", type=float, help="Target output power in dBm")
    parser.add_argument("--f0", type=float, required=True, help="Center frequency in Hz")
    parser.add_argument("--vdd", type=float, required=True, help="Supply voltage in V")
    parser.add_argument("--r-load", type=float, required=True, help="Load resistance in ohm")
    parser.add_argument(
        "--v-pk-max",
        type=float,
        default=None,
        help="Allowed RF peak voltage swing across the load in V. Defaults to VDD.",
    )
    parser.add_argument("--f-max-pad", type=float, default=None, help="Pad frequency limit in Hz")
    parser.add_argument("--i-rms-max", type=float, default=None, help="Output RMS current limit in A")
    parser.add_argument("--i-pk-max", type=float, default=None, help="Output peak current limit in A")
    parser.add_argument("--idc-max", type=float, default=None, help="DC current limit in A")
    parser.add_argument(
        "--classes",
        default="A,AB,B,C",
        help="Comma-separated PA classes for Idc feasibility estimates",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pout_w = args.pout_w if args.pout_w is not None else dbm_to_w(args.pout_dbm)
    pout_dbm = w_to_dbm(pout_w)
    v_pk_max = args.v_pk_max if args.v_pk_max is not None else args.vdd
    pout_voltage_limited_w = v_pk_max**2 / (2.0 * args.r_load)
    v_rms = math.sqrt(pout_w * args.r_load)
    v_pk = math.sqrt(2.0) * v_rms
    i_rms = v_rms / args.r_load
    i_pk = v_pk / args.r_load
    r_device_ideal = args.vdd**2 / (2.0 * pout_w)

    classes = [c.strip().upper() for c in args.classes.split(",") if c.strip()]
    idc_by_class = {
        c: pout_w / (ETA_GUESS.get(c, 0.45) * args.vdd) for c in classes
    }

    checks = {
        "frequency_limit_pass": (
            None if args.f_max_pad is None else args.f0 <= args.f_max_pad
        ),
        "voltage_swing_limit_pass": v_pk <= v_pk_max,
        "i_rms_limit_pass": (
            None if args.i_rms_max is None else i_rms <= args.i_rms_max
        ),
        "i_pk_limit_pass": (
            None if args.i_pk_max is None else i_pk <= args.i_pk_max
        ),
        "idc_limit_pass_by_class": {
            c: (None if args.idc_max is None else idc <= args.idc_max)
            for c, idc in idc_by_class.items()
        },
    }

    hard_fail = any(v is False for v in checks.values() if isinstance(v, bool))
    hard_fail = hard_fail or any(
        v is False for v in checks["idc_limit_pass_by_class"].values()
    )
    status = "fail" if hard_fail else "pass"
    if status == "pass":
        margins = []
        if args.i_pk_max:
            margins.append(i_pk / args.i_pk_max)
        if args.i_rms_max:
            margins.append(i_rms / args.i_rms_max)
        if args.idc_max and idc_by_class:
            margins.append(min(idc_by_class.values()) / args.idc_max)
        margins.append(v_pk / v_pk_max)
        if any(m > 0.8 for m in margins):
            status = "marginal"

    result = {
        "status": status,
        "pout_w": pout_w,
        "pout_dbm": pout_dbm,
        "pout_voltage_limited_w": pout_voltage_limited_w,
        "pout_voltage_limited_dbm": w_to_dbm(pout_voltage_limited_w),
        "v_rms": v_rms,
        "v_pk": v_pk,
        "v_pk_max": v_pk_max,
        "i_rms": i_rms,
        "i_pk": i_pk,
        "r_device_ideal_ohm": r_device_ideal,
        "idc_est_by_class_amp": idc_by_class,
        "checks": checks,
        "notes": [
            "Large required inductors or transformers still need passive-scope review.",
            "This is a feasibility precheck, not a substitute for RF simulation.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
