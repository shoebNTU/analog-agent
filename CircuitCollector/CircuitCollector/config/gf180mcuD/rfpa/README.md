# GF180MCU-D RF PA Configs

This directory contains seed RF power-amplifier configs for the GF180MCU-D
CircuitCollector overlay. Each config follows the same selection pattern used
by the opamp configs:

```toml
[type]
name = "rfpa"

[rfpa]
name = "<directory under circuits/rfpa>"
```

The matching netlist template is expected at:

```text
CircuitCollector/circuits/rfpa/<rfpa.name>/netlist.j2
```

## Validation Status

| Config | Template | Status | Intended use |
| --- | --- | --- | --- |
| `class_ab_single_ended.toml` | `class_ab_single_ended/netlist.j2` | `runnable_seed` | Current single-ended Class-AB seed for 250 MHz, pad-limited RFPA experiments. |
| `two_stage_single_ended.toml` | `two_stage_single_ended/netlist.j2` | `runnable_idealized_seed` | Textbook-style driver plus final-stage PA using the standard single-ended RFPA testbench. |
| `differential_cascode_transformer.toml` | `differential_cascode_transformer/netlist.j2` | `runnable_idealized_seed` | Textbook-style differential cascode/neutralization seed adapted through an idealized passive coupled-inductor transformer. |
| `class_a_single_ended.toml` | `class_a_single_ended/netlist.j2` | `runnable_idealized_seed` | Linear single-ended Class-A topology candidate. |
| `class_b_differential.toml` | `class_b_differential/netlist.j2` | `runnable_idealized_seed` | Differential/push-pull topology candidate; requires a differential RF testbench and combiner model. |
| `class_c_tuned.toml` | `class_c_tuned/netlist.j2` | `runnable_idealized_seed` | Tuned Class-C topology candidate for constant-envelope operation. |
| `class_e_switching.toml` | `class_e_switching/netlist.j2` | `runnable_idealized_seed` | Switch-mode Class-E topology candidate; requires waveform-stress validation. |
| `class_f_harmonic_tuned.toml` | `class_f_harmonic_tuned/netlist.j2` | `runnable_idealized_seed` | Harmonic-tuned Class-F topology candidate; requires harmonic termination synthesis. |

Runnable idealized seeds intentionally remain exploratory: they can exercise
the RFPA parser/testbench path, but contain ideal bias, balun/combiner, or
schematic seed matching assumptions. They are not passive/layout signoff.

Former scaffold configs promoted to runnable idealized seeds now set:

```toml
template_only = false
simulation_enabled = true
validation_status = "runnable_idealized_seed"
```

These files can exercise the standard RFPA smoke-test path, but remain idealized. Class-specific checks such as differential common-mode validation, conduction angle, switch waveform stress, finite-Q harmonic termination, and signoff load-pull closure must be treated as advisory until implemented in the runner/parser.

## Current RFPA Runner Coverage

The active RFPA runner can exercise the single-ended RFPA flow used by the
Class-AB seed:

- DC current and power.
- Large-signal transient Pout, gain, PAE, and drain efficiency.
- Waveform-derived H2/H3 estimates.
- AC-estimated S11, S22, Rollett K, and mu.
- Input-power sweep for P1dB, AM/AM, and AM/PM.
- Load-mismatch sweep for VSWR-like stress checks.

For scaffold-only classes, leave `simulation_enabled = false` until the runner
and testbench are made class-aware.
