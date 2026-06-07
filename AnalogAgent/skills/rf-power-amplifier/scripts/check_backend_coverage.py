#!/usr/bin/env python3
"""Check RFPA backend asset coverage for CircuitCollector-style mappings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import tomllib


TOPOLOGIES = {
    "class_a_single_ended": {
        "config": "config/gf180mcuD/rfpa/class_a_single_ended.toml",
        "netlist": "circuits/rfpa/class_a_single_ended/netlist.j2",
    },
    "class_ab_single_ended": {
        "config": "config/gf180mcuD/rfpa/class_ab_single_ended.toml",
        "netlist": "circuits/rfpa/class_ab_single_ended/netlist.j2",
    },
    "two_stage_single_ended": {
        "config": "config/gf180mcuD/rfpa/two_stage_single_ended.toml",
        "netlist": "circuits/rfpa/two_stage_single_ended/netlist.j2",
    },
    "class_b_differential": {
        "config": "config/gf180mcuD/rfpa/class_b_differential.toml",
        "netlist": "circuits/rfpa/class_b_differential/netlist.j2",
    },
    "differential_cascode_transformer": {
        "config": "config/gf180mcuD/rfpa/differential_cascode_transformer.toml",
        "netlist": "circuits/rfpa/differential_cascode_transformer/netlist.j2",
    },
    "class_c_tuned": {
        "config": "config/gf180mcuD/rfpa/class_c_tuned.toml",
        "netlist": "circuits/rfpa/class_c_tuned/netlist.j2",
    },
    "class_e_switching": {
        "config": "config/gf180mcuD/rfpa/class_e_switching.toml",
        "netlist": "circuits/rfpa/class_e_switching/netlist.j2",
    },
    "class_f_harmonic_tuned": {
        "config": "config/gf180mcuD/rfpa/class_f_harmonic_tuned.toml",
        "netlist": "circuits/rfpa/class_f_harmonic_tuned/netlist.j2",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend-root",
        required=True,
        help="Path to the backend package root, e.g. CircuitCollector/CircuitCollector",
    )
    args = parser.parse_args()

    root = Path(args.backend_root).expanduser().resolve()
    results = {}
    for name, paths in TOPOLOGIES.items():
        config = root / paths["config"]
        netlist = root / paths["netlist"]
        config_exists = config.exists()
        netlist_exists = netlist.exists()

        config_rfpa = {}
        enabled = None
        validation_status = None
        if config_exists:
            try:
                with config.open("rb") as file_obj:
                    config_data = tomllib.load(file_obj)
                config_rfpa = config_data.get("rfpa", {})
                enabled = config_rfpa.get("simulation_enabled")
                validation_status = config_rfpa.get("validation_status")
            except tomllib.TOMLDecodeError as exc:
                validation_status = f"toml_error: {exc}"

        if config_exists and netlist_exists and enabled is True:
            if validation_status == "runnable_seed":
                status = "runnable_core_smoke_test_required"
            elif validation_status == "runnable_idealized_seed":
                status = "runnable_idealized_smoke_test_required"
            else:
                status = "enabled_unknown_validation_smoke_test_required"
        elif config_exists and netlist_exists and enabled is False:
            status = "scaffold_only"
        elif config_exists and netlist_exists:
            status = "assets_present_enablement_unknown"
        elif config_exists or netlist_exists:
            status = "partial_assets"
        else:
            status = "missing"
        results[name] = {
            "status": status,
            "config": str(config),
            "config_exists": config_exists,
            "simulation_enabled": enabled,
            "validation_status": validation_status,
            "netlist": str(netlist),
            "netlist_exists": netlist_exists,
        }

    print(json.dumps({"backend_root": str(root), "topologies": results}, indent=2))


if __name__ == "__main__":
    main()
