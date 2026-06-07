# CircuitCollector RF PA Backend Adapter

Use this file only when the task will simulate through the local
CircuitCollector RFPA backend. The generic RF PA skill must not assume these
paths or template names when another simulator, a hand netlist, or a purely
analytical design task is being used.

Common GF180MCU-D backend root in this shared bundle:

```text
share_GF180_Analog/CircuitCollector/CircuitCollector
```

## Local Mapping

These paths are expected relative to the CircuitCollector package root. Run
`scripts/check_backend_coverage.py --backend-root <CircuitCollector root>` before
claiming any row is runnable.

| Generic topology | Local template key | Expected config path | Expected netlist path | Status rule |
|---|---|---|---|---|
| Class-A single-ended | `rfpa/class_a_single_ended` | `config/gf180mcuD/rfpa/class_a_single_ended.toml` | `circuits/rfpa/class_a_single_ended/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |
| Class-AB single-ended | `rfpa/class_ab_single_ended` | `config/gf180mcuD/rfpa/class_ab_single_ended.toml` | `circuits/rfpa/class_ab_single_ended/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |
| Two-stage single-ended | `rfpa/two_stage_single_ended` | `config/gf180mcuD/rfpa/two_stage_single_ended.toml` | `circuits/rfpa/two_stage_single_ended/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |
| Class-B differential | `rfpa/class_b_differential` | `config/gf180mcuD/rfpa/class_b_differential.toml` | `circuits/rfpa/class_b_differential/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |
| Differential cascode transformer | `rfpa/differential_cascode_transformer` | `config/gf180mcuD/rfpa/differential_cascode_transformer.toml` | `circuits/rfpa/differential_cascode_transformer/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |
| Class-C tuned | `rfpa/class_c_tuned` | `config/gf180mcuD/rfpa/class_c_tuned.toml` | `circuits/rfpa/class_c_tuned/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |
| Class-E switching | `rfpa/class_e_switching` | `config/gf180mcuD/rfpa/class_e_switching.toml` | `circuits/rfpa/class_e_switching/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |
| Class-F harmonic tuned | `rfpa/class_f_harmonic_tuned` | `config/gf180mcuD/rfpa/class_f_harmonic_tuned.toml` | `circuits/rfpa/class_f_harmonic_tuned/netlist.j2` | runnable only if files exist, config enabled, and smoke test passes |

## Readiness Gate

Before running a CircuitCollector simulation, run:

```bash
python3 skills/rf-power-amplifier/scripts/check_backend_coverage.py \
  --backend-root ../../CircuitCollector/CircuitCollector
```

Then inspect the selected config or API metadata for:

```toml
[rfpa]
simulation_enabled = true/false
validation_status = "..."
```

- If `simulation_enabled = true` and `validation_status = "runnable_seed"`, the
  config may be used as core simulation evidence after a smoke test.
- If `simulation_enabled = true` and
  `validation_status = "runnable_idealized_seed"`, the config may be used for
  topology exploration and parser testing; mark idealized elements as advisory.
- If `simulation_enabled = false`, use the topology only for first-pass sizing
  and candidate ranking.
- If the config or template is missing, report it as `missing_backend_mapping`.
- If prior output files exist but source config/netlist files are missing, report
  `historical_output_only`; it is evidence that experiments ran, not reusable
  backend coverage.

## Backend Binding Output

```text
RF PA BACKEND PROFILE
=====================
Backend       : CircuitCollector
Topology      : <>
Template key  : <>
Config path   : <>
Netlist path  : <>
Status        : runnable_seed / scaffold_only / missing_backend_mapping / custom
Evidence use  : simulation evidence / sizing only / advisory
```

## Smoke-Test Metrics

A CircuitCollector RFPA smoke test should request at least:

```text
idc_total, pdc_w, pout_w, pout_dbm, gain_db, pae, drain_efficiency,
iout_rms, iout_pk_est, h2_dbc, h3_dbc,
s11_db, s21_db, s12_db, s22_db, stability_k, stability_mu,
p1db_dbm, amam_at_nominal_db, ampm_at_nominal_deg
```

When the API is reachable, run:

```bash
python3 skills/rf-power-amplifier/scripts/smoke_test_backend.py \
  --backend-root ../../CircuitCollector/CircuitCollector \
  --api-url http://localhost:8001/simulate/
```

For a fast render/parser smoke test before expensive sweeps:

```bash
python3 skills/rf-power-amplifier/scripts/smoke_test_backend.py \
  --backend-root ../../CircuitCollector/CircuitCollector \
  --api-url http://localhost:8001/simulate/ \
  --quick
```

If the HTTP API worker is busy but the backend Python environment is available,
run the same smoke test in-process:

```bash
PATH=/foss/tools/ngspice/bin:$PATH \
LD_LIBRARY_PATH=/foss/tools/ngspice/lib:$LD_LIBRARY_PATH \
python3 skills/rf-power-amplifier/scripts/smoke_test_backend.py \
  --backend-root <container_share_root>/CircuitCollector/CircuitCollector \
  --quick \
  --direct
```

If the API is down, report `api_unreachable` and keep the status at
`*_smoke_test_required`.
