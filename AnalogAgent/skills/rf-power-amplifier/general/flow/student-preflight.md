# RF PA Student Preflight

Use this before class selection or transistor sizing, especially when the user
provides only specs and no netlist.

## Purpose

Prevent a beginner from sizing an impossible or underspecified RF PA. The goal
is to turn vague specs into a bounded schematic simulation task.

## Step 1 - Resolve The Design Boundary

Classify these before doing any sizing:

| Item | Required decision |
|---|---|
| Reference plane | on-chip output node, pad, package pin, board load, or custom |
| Passive scope | schematic only, on-chip, package/bondwire, off-chip, mixed, EM extracted |
| Load model | real test load, transformed load, ideal load-pull target, or package/board load |
| Active metrics | which specs can pass/fail with the modeled elements |
| Advisory metrics | which specs need unmodeled package/off-chip/layout elements |

If unspecified, declare this conservative schematic-only boundary:

```text
Reference plane = schematic_output_node
Passive_scope = schematic_available_only
Active checks = voltage/current stress, nominal Pout/gain/PAE/efficiency,
                harmonics, compression/AM-AM/AM-PM if requested, and core stability
Advisory checks = final external S11/S22, load mismatch ruggedness,
                  off-chip/package match, EM/layout closure
```

## Step 2 - Run The Feasibility Precheck

Use `scripts/rfpa_preflight.py` or equivalent Python calculations. Check:

- `f0 <= f_max_pad`
- `Pout_target` implied `Vrms`, `Vpk`, `Irms`, and `Ipk` into the stated load
- textbook voltage-limited maximum `Pout_max = Vpk_max^2 / (2 * R_load)`,
  using `Vpk_max = VDD` unless the topology allows and justifies a different
  swing limit
- `Ipk` and `Irms` against output/pad current limits
- `Idc ~= Pout / (eta_guess * VDD)` for plausible PA classes
- Required ideal device load `R_device ~= VDD^2 / (2 * Pout)`
- Whether the match/passive values are likely schematic/on-chip or package/off-chip candidates

Do not proceed to transistor sizing if hard voltage/current/frequency limits
are violated. Instead, lower `Pout`, change load/reference plane, or request
permission to use package/off-chip matching.

Example command shape, using placeholders from the active spec:

```bash
python skills/rf-power-amplifier/scripts/rfpa_preflight.py \
  --f0 <Hz> --vdd <V> --pout-w <W> --r-load <ohm> \
  --f-max-pad <Hz-if-active> --i-rms-max <A-if-active> \
  --i-pk-max <A-if-active> --idc-max <A-if-active> \
  --classes <comma-separated-candidates>
```

If the script returns `marginal`, proceed only with explicit margin reporting.
For example, a design can pass RMS current but still be close to the peak
current limit.

## Step 3 - Choose Candidate Classes

Use this beginner-safe candidate starting point:

```text
High linearity or unknown modulation -> A, AB
Moderate linearity, efficiency desired -> AB, B
Constant-envelope narrowband -> C, optionally E/F only if harmonic waveform
                                  stress and passive scope are modeled
```

If the user asks for `PA_class = auto`, rank candidates but simulate only those
with runnable backend implementations. Scaffold-only classes can be
recommended, not verified.

## Step 4 - Declare The Simulation Contract

Before sizing, print:

```text
RF PA STUDENT PREFLIGHT
=======================
Feasibility      : pass / fail / marginal
Reference plane  : <>
Passive scope    : <>
Active checks    : <>
Advisory checks  : <>
Candidate classes: <>
Runnable backend : <>
Main risks       : <>
Next action      : size / ask for missing scope / relax spec / add model
```

This output is a gate. Do not proceed to initial sizing until it is printed.
