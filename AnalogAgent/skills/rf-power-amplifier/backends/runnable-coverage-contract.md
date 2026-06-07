# Runnable Backend Coverage Contract

Use this file before claiming that an RF PA topology has fully runnable backend
coverage. A documented topology flow is not enough; the backend must have
source assets, parser coverage, and a passing smoke test.

## Required Assets

For each topology/backend pair, verify:

| Asset | Requirement |
|---|---|
| Config | Names topology, device/process binding, analyses, spec list, enabled flag |
| Netlist/template | Instantiates ports, devices, bias, matching networks, and measurement hooks |
| Model binding | Points to valid PDK models or an explicit idealized model declaration |
| Parameter map | Exposes sizing, bias, passive, drive, load, and analysis knobs |
| Parser/spec library | Extracts OP, S-parameters, large-signal power, harmonics, compression, and reliability |
| Smoke test | Runs with nominal parameters and returns parseable active metrics |

## Required Analysis Coverage

Classify each row as `implemented`, `advisory`, `out_of_scope`, or `missing`:

| Analysis | Evidence required |
|---|---|
| DC/OP | Idc, Pdc, device regions/stress, bias sanity |
| S-parameter | S11/S21/S12/S22, K/mu or equivalent, parser sanity |
| Large signal | Pout, gain, PAE, drain efficiency at nominal drive |
| Harmonics | H2/H3 or declared not relevant |
| Compression | P1dB or compression/backoff sweep |
| AM/AM and AM/PM | Nominal and swept values or declared not relevant |
| Load mismatch/load-pull | Sweep or advisory closure contract |
| PVT/temperature | Required only when active in the spec |

## Backend Status Labels

```text
runnable_full       all required active analyses implemented and smoke-tested
runnable_core       OP/S-param/large-signal/harmonics implemented; advanced analyses advisory
scaffold_only       flow exists but source assets or core analyses are missing
historical_output   prior outputs exist but reusable source assets are missing
missing             no backend mapping
```

Only `runnable_full` and `runnable_core` may be used as simulation evidence in a
design review. `scaffold_only`, `historical_output`, and `missing` are sizing or
planning evidence only.

