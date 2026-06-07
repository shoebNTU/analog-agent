#!/usr/bin/env python3
"""Run RFPA backend smoke tests through a CircuitCollector-compatible backend."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import request
from urllib.error import HTTPError, URLError


TOPOLOGIES = [
    "class_a_single_ended",
    "class_ab_single_ended",
    "two_stage_single_ended",
    "class_b_differential",
    "differential_cascode_transformer",
    "class_c_tuned",
    "class_e_switching",
    "class_f_harmonic_tuned",
]

SPEC_KEYS = [
    "idc_total",
    "pdc_w",
    "pout_w",
    "pout_dbm",
    "gain_db",
    "pae",
    "drain_efficiency",
    "iout_rms",
    "iout_pk_est",
    "h2_dbc",
    "h3_dbc",
    "s11_db",
    "s21_db",
    "s12_db",
    "s22_db",
    "stability_k",
    "stability_mu",
    "p1db_dbm",
    "pin_at_p1db_dbm",
    "amam_at_nominal_db",
    "ampm_at_nominal_deg",
    "idc_limit_pass",
    "iout_rms_limit_pass",
    "iout_pk_limit_pass",
]

QUICK_SPEC_KEYS = [
    "idc_total",
    "pdc_w",
    "pout_w",
    "pout_dbm",
    "gain_db",
    "pae",
    "drain_efficiency",
    "iout_rms",
    "iout_pk_est",
    "h2_dbc",
    "h3_dbc",
    "s11_db",
    "s21_db",
    "s12_db",
    "s22_db",
    "stability_k",
    "stability_mu",
    "idc_limit_pass",
    "iout_rms_limit_pass",
    "iout_pk_limit_pass",
]


def post_json(url: str, payload: dict, timeout: float) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def decode_http_error(exc: HTTPError) -> dict:
    body = exc.read().decode("utf-8", errors="replace")
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        parsed = body
    return {
        "status": "api_error",
        "http_status": exc.code,
        "reason": exc.reason,
        "detail": parsed,
    }


def jsonable(value):
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, dict):
        return {key: jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    return value


def summarize_specs(specs: dict, spec_keys: list[str]) -> dict:
    parseable = {key: specs.get(key) for key in spec_keys if key in specs}
    non_null = {key: value for key, value in parseable.items() if value is not None}
    return {
        "parseable_metric_count": len(non_null),
        "parseable_metrics": jsonable(parseable),
    }


def read_tail(path: Path, lines: int = 40) -> str | None:
    if not path.exists():
        return None
    text = path.read_text(errors="replace")
    return "\n".join(text.splitlines()[-lines:])


def output_diagnostics(root: Path, output_dir: str, topology: str) -> dict:
    out = root / output_dir
    files = sorted(p.name for p in out.glob("*")) if out.exists() else []
    return {
        "output_dir": str(out),
        "output_files": files,
        "log_tail": read_tail(out / f"{topology}.log"),
    }


def run_direct(root: Path, config_rel: Path, output_dir: str, spec_keys: list[str], params: dict) -> dict:
    sys.path.insert(0, str(root.parent))
    from CircuitCollector.sim_api import SimulationAPI

    api = SimulationAPI(
        base_config_path=config_rel,
        output_dir=Path(output_dir),
        spec_list=spec_keys,
    )
    return api.run(params)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend-root",
        required=True,
        help="CircuitCollector package root that contains config/gf180mcuD/rfpa",
    )
    parser.add_argument("--api-url", default="http://localhost:8001/simulate/")
    parser.add_argument("--output-dir-prefix", default="output/rfpa/smoke")
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--topology", action="append", choices=TOPOLOGIES)
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Run CircuitCollector.sim_api.SimulationAPI in-process instead of calling the HTTP API.",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Disable expensive power/load sweeps; validates render, OP, S-param, transient, and parser path.",
    )
    parser.add_argument(
        "--absolute-config-path",
        action="store_true",
        help="Send absolute config paths. Default sends paths relative to backend root.",
    )
    args = parser.parse_args()

    root = Path(args.backend_root).expanduser().resolve()
    selected = args.topology or TOPOLOGIES
    results = {}

    for topology in selected:
        config_rel = Path("config/gf180mcuD/rfpa") / f"{topology}.toml"
        config = root / config_rel
        config_payload = str(config if args.absolute_config_path else config_rel)
        params = {}
        if args.quick:
            params.update(
                {
                    "measure_power_sweep": False,
                    "measure_load_pull": False,
                    "measure_modulated": False,
                }
            )
        else:
            params["measure_power_sweep"] = True

        spec_keys = QUICK_SPEC_KEYS if args.quick else SPEC_KEYS
        payload = {
            "base_config_path": config_payload,
            "output_dir": f"{args.output_dir_prefix}/{topology}",
            "spec_list": spec_keys,
            "params": params,
        }
        try:
            if args.direct:
                response = run_direct(
                    root,
                    config_rel,
                    f"{args.output_dir_prefix}/{topology}",
                    spec_keys,
                    params,
                )
            else:
                response = post_json(args.api_url, payload, args.timeout)
            specs = response.get("specs", {})
            summary = summarize_specs(specs, spec_keys)
            results[topology] = {
                "status": "ran" if summary["parseable_metric_count"] else "no_parseable_metrics",
                **summary,
                "error": response.get("error"),
            }
            if not summary["parseable_metric_count"]:
                results[topology]["diagnostics"] = output_diagnostics(
                    root, f"{args.output_dir_prefix}/{topology}", topology
                )
        except HTTPError as exc:
            results[topology] = decode_http_error(exc)
        except URLError as exc:
            results[topology] = {"status": "api_unreachable", "error": str(exc)}
        except Exception as exc:
            results[topology] = {"status": "failed", "error": str(exc)}

    print(json.dumps({"backend_root": str(root), "results": results}, indent=2))


if __name__ == "__main__":
    main()
