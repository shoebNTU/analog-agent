---
name: rf-power-amplifier
description: >
  RF power amplifier design workflow for integrated CMOS/RFIC PAs. Use when
  sizing, reviewing, or debugging RF PAs; selecting Class A/AB/B/C/E/F/G/H;
  estimating output power, load transformation, drain efficiency, PAE, gain,
  linearity, AM/AM, AM/PM, stability, neutralization, or load-pull/harmonic-
  balance simulation plans. Generic across CMOS/RFIC processes when the
  process profile, device limits, and simulator backend are supplied.
---

# RF Power Amplifier Design Skill

> Reference basis: JKU RFIC course, Section 8 "Power Amplifiers".
> Use this as procedural guidance, not as a substitute for large-signal
> simulation, PDK limits, layout parasitics, EM extraction, or load-pull data.
> Keep the core flow process- and simulator-neutral. Load process profiles,
> simulator adapters, and example specs only when the current task names them.

## Rules

1. Execute the design flow in order. Do not jump straight to transistor widths.
2. All calculations must be done in Python. Never compute RF power, dBm, load
   transforms, Q, efficiency, or impedance values mentally.
3. Treat PA design as large-signal. Small-signal gain is useful, but final
   decisions require harmonic-balance/transient-RF/load-pull style verification.
4. Check device voltage/current reliability before optimizing performance.
5. Use the diagnosis reference for failures. Do not improvise fixes when a
   fault tree exists.
6. State assumptions explicitly: topology, class, supply, target frequency,
   target Pout, load, input drive, modulation/PAPR, duty cycle, and matching Q.
7. Separate on-chip-core requirements from package/board requirements. If the
   task only simulates on-chip circuit elements, do not make final external
   reference-plane S11/S22, VSWR ruggedness, off-chip matching, pad/ESD
   parasitics, or EM extraction hard pass/fail items. Report them as advisory
   or residual system-level risks unless those elements are explicitly modeled.
8. If passive implementation is unspecified, limit active claims to schematic
   elements that are actually modeled. Suggest on-chip/package/off-chip passive
   partitioning, but mark unmodeled passives and reference-plane closure as
   advisory or residual.
9. Poor S11/S22 must always trigger a match-closure decision. If the reference
   plane and matching/pad/package elements are modeled, return loss is active
   and must be synthesized/optimized before SUCCESS. If they are not modeled,
   keep the core result eligible for SUCCESS only after writing a concrete
   match-closure contract: missing model/scope, required template/API features,
   bounded schematic improvements attempted, and the simulations needed to make
   S11/S22 active.

## Spec Profiles

- The skill accepts any complete RF PA spec supplied by the user; it is not
  tied to a particular spec file.
- For an on-chip-core-only task, active checks are limited to modeled schematic
  elements: current/voltage stress, nominal Pout/gain/PAE/efficiency,
  harmonics, requested compression/AM-AM/AM-PM, finite-Q schematic passives,
  and core stability estimates.
- For full-PA planning, include package, board, pad, ESD, EM, and off-chip
  matching expectations only when those reference-plane elements are modeled or
  explicitly supplied. Otherwise classify them as advisory/residual.
- Optional local templates may exist in the repository, but they are examples
  or convenience forms. Do not inherit numeric targets from a template unless
  the user provides that template as the active spec.

## Architecture

```
general/
  flow/
    student-preflight.md            Beginner-safe feasibility and scope gate
    spec-understanding.md          Validate RF PA specs and declared assumptions
    topology-understanding.md      Identify class, topology, matching networks
    simulation-verification.md     Verify large-signal PA results
    design-review.md               Final PA report format
  reference/
    pa-metrics.md                  Equations and conversions
    pa-classes.md                  Class selection guidance
    class-auto-selection.md        Auto class candidate ranking
    matching-and-load-pull.md      Load transform and load-pull workflow
    stability-neutralization.md    Stability, S12, cascode, neutralization
    root-cause-diagnosis.md        Fault trees for PA failures
    source-map.md                  Reference-backed coverage map
    rfpa-equation-framework.md     Shared PA equations and sign conventions

process/
    <process>.md                   Optional PDK/device/reliability profile

backends/
    <backend>.md                   Optional simulator/API mapping
    runnable-coverage-contract.md  Required backend assets and smoke tests

examples/
    *.md                           Non-binding example specs and notes

circuit-specific/<topology>/
    *-equation.md                  Topology-specific first-pass equations
    *-design-flow.md               Topology-specific sizing and validation steps

scripts/
    rfpa_preflight.py              Deterministic first-pass feasibility calculator
    check_backend_coverage.py      Checks backend config/netlist asset presence
    smoke_test_backend.py          Runs advised backend smoke tests through API
```

### Supported Circuit-Specific Flows

| PA class/topology | Directory | Backend mapping |
|---|---|---|
| Class-A single-ended | `circuit-specific/class-a-single-ended/` | See selected backend adapter |
| Class-AB single-ended | `circuit-specific/class-ab-single-ended/` | See selected backend adapter |
| Two-stage single-ended | `circuit-specific/two-stage-single-ended/` | See selected backend adapter |
| Class-B differential | `circuit-specific/class-b-differential/` | See selected backend adapter |
| Differential cascode transformer | `circuit-specific/differential-cascode-transformer/` | See selected backend adapter |
| Class-C tuned | `circuit-specific/class-c-tuned/` | See selected backend adapter |
| Class-E switching | `circuit-specific/class-e-switching/` | See selected backend adapter |
| Class-F harmonic tuned | `circuit-specific/class-f-harmonic-tuned/` | See selected backend adapter |

## Design Flow

```
User gives PA netlist/specs
        |
        v
[1] SPEC UNDERSTANDING
    Read: general/flow/spec-understanding.md
    Gate: required RF PA fields present, or STOP

[1P] PROCESS/BACKEND BINDING
    If a process, PDK, simulator, or local API is named, read only the matching
    process/<process>.md and/or backends/<backend>.md profile. Otherwise keep
    device limits and simulator paths as explicit assumptions, not defaults.

[1A] STUDENT PREFLIGHT
    Read: general/flow/student-preflight.md
    Run: scripts/rfpa_preflight.py or equivalent Python calculations
    Gate: feasibility, reference plane, passive scope, and active/advisory
          metrics declared before sizing

[2] TOPOLOGY UNDERSTANDING
    Read: general/flow/topology-understanding.md
    Identify: class, single-ended/differential, cascode, drivers, matching

[2A] CLASS AUTO-SELECTION (only if PA_class = auto or Candidate_classes exists)
    Read:
      general/reference/pa-classes.md
      general/reference/class-auto-selection.md
    Rank A/AB/B/C by reliability, linearity, efficiency, matching feasibility,
    and implementation risk. Include E/F/G/H only when explicitly in scope.
    If PA_class is fixed, obey it but report conflicts and alternatives.

[3] INITIAL DESIGN
    Read as needed:
      general/reference/source-map.md
      general/reference/rfpa-equation-framework.md
      general/reference/pa-metrics.md
      general/reference/pa-classes.md
      general/reference/matching-and-load-pull.md
      general/reference/stability-neutralization.md
      circuit-specific/<selected-topology>/*-equation.md
      circuit-specific/<selected-topology>/*-design-flow.md
    Derive first-pass load, current, voltage swing, device stress, passive
    implementation scope, matching, and bias. Use Python for every calculation.

[4] SIMULATION & VERIFICATION
    Read: general/flow/simulation-verification.md
    If a backend is selected, read: backends/runnable-coverage-contract.md
    and the selected backend adapter before trusting simulation evidence.
    Verify OP, S-parameters/stability, large-signal Pout/gain/PAE, compression,
    AM/AM, AM/PM, harmonics, transient waveform, reliability, and the
    S11/S22 active/advisory match-closure decision.

[5] ROOT-CAUSE DIAGNOSIS
    If any spec fails, read: general/reference/root-cause-diagnosis.md
    Apply the relevant fault tree, update sizing/matching/bias, and return to [3].
    If PA_class=auto and the failure indicates topology limitation, return to
    [2A] and try the next runnable topology instead of repeatedly tuning the
    same circuit.

[6] DESIGN REVIEW
    Read: general/flow/design-review.md
    Produce the strict report with specs, sizing, matching, simulation setup,
    iteration history, and residual risks.
```

## Simulation Loop

```
iteration_count = 0
MAX_ITERATIONS = 8

LOOP:
  iteration_count += 1

  [1A] Confirm feasibility/scope has not changed
  [3] Execute selected class-specific design flow
  [4] Simulate and verify active on-chip/core or full-PA targets
      IF all active specs pass and no hard reliability/stability failure:
        -> BREAK -> [6] Design Review (SUCCESS)
      ELIF iteration_count >= MAX_ITERATIONS:
        -> BREAK -> [6] Design Review (TIMEOUT)
      ELIF PA_class = auto AND diagnosis marks "topology_limited":
        -> [2A] CLASS AUTO-SELECTION -> try next runnable topology
      ELIF active S11/S22 fail:
        -> [5] Root-cause diagnosis -> synthesize/optimize modeled match
      ELIF advisory S11/S22 are poor:
        -> write match-closure contract; optionally run bounded schematic
           damping/match attempts without claiming package/board closure
      ELSE:
        -> [5] Root-cause diagnosis -> apply fix -> LOOP
```

Always fix hard reliability failures before optimizing Pout, gain, PAE, or
matching. Do not change PA class inside the loop unless `PA_class = auto` or
the user approves a class change. Under `PA_class = auto`, topology changes are
required when the diagnosis says the present topology cannot satisfy an active
constraint after a bounded local search.

### Feedback-Driven Auto Topology Selection

When `PA_class = auto`, maintain a candidate table for every runnable local
backend implementation and update it after each simulation:

```text
candidate | status | active passes | active failures | root cause | next action
```

Use these escalation triggers:

- `K <= 1` or `mu <= 1` after damping/matching attempts:
  try a topology with better isolation, such as two-stage, cascode, differential,
  or neutralized transformer-coupled PA.
- Nominal Pout/gain/PAE pass but P1dB or AM/AM fails:
  reduce drive/interstage gain, increase output-stage headroom, or try a
  topology with a driver/final-stage split.
- Harmonics fail after nominal operation is stable:
  add or retune harmonic terminations; if the current topology has no modeled
  harmonic network, try a harmonic-capable implementation or mark the backend
  incomplete.
- Final S11/S22 fail and the full reference plane is modeled:
  keep the topology if it otherwise passes, but mark `network_incomplete` and
  optimize input/output matching before accepting SUCCESS.
- Final S11/S22 fail only because package/off-chip/pad/EM elements are absent:
  mark `advisory_limited`, do not switch class solely for return loss, and
  produce the match-closure contract in the review.
- Load-mismatch current/voltage fails and mismatch is active:
  lower output-network Q, use load-pull-selected impedance, or try transformer/
  package/off-chip matching when those elements are modeled.
- A scaffold-only topology may be recommended but must not replace a runnable
  candidate as simulated evidence.

Select the next topology by active-spec risk order:

```text
reliability > core stability > linearity/compression > harmonics >
Pout/gain/PAE > advisory match/load/EM risks
```

The selected topology is the best runnable candidate for the next iteration,
not a successful design, until all active metrics pass.

## Supported Starting Points

- Single-ended common-source PA with LC/transformer matching.
- Differential common-source PA.
- Differential cascode PA for voltage stress handling.
- Driver + output-stage PA chains.
- Linear Class A/AB/B PAs.
- High-efficiency/switching Class C/E/F-style explorations, with a warning that
  waveform/harmonic tuning dominates and closed-form sizing is only a starting
  point.

## Mandatory Calculations

Before simulation, compute at least:

- Student preflight: load current/voltage swing, pad-frequency check, current
  limit check, class-wise estimated DC current, and ideal device load.
- Required load at the active device from `Pout`, `VDD`, and swing limit.
- Impedance transformation from the specified external/load reference plane to
  the device load.
- DC power budget and ideal drain efficiency / PAE estimate.
- Peak voltage/current stress, including cascode stack sharing if present.
- Matching-network Q, component values, and expected bandwidth.
- Passive implementation scope: on-chip lumped, package/bondwire, off-chip,
  EM-extracted, or ideal/unspecified.
- Input drive required from target gain and compression margin.
- Stability risk from reverse isolation, Miller capacitance, and layout/package
  parasitics.

## Comprehensive Coverage Gate

Do not call an RF PA sizing/review comprehensive unless the report explicitly
covers, or marks out of scope, each item below:

- Efficiency: Pdc, drain efficiency, PAE, input-drive impact, and passive loss.
- Nonlinearity: compression, AM/AM, AM/PM, modulation/PAPR implications, and
  any EVM/ACLR/IM3 targets.
- Class behavior: conduction angle or switching/tuned operation, class tradeoff,
  and why the selected class matches the signal and reliability constraints.
- Load and matching: target device load, reference plane, finite-Q matching,
  load-pull/source-pull status, and return-loss activation/advisory decision.
- Stability and neutralization: K/mu or equivalent stability evidence, S12 or
  Miller feedback risk, cascode/neutralization/damping choice, and out-of-band
  sweep scope.
- Reliability: voltage stress, current stress, duty cycle/thermal assumptions,
  PVT/load-mismatch stress, and whether layout/package parasitics are modeled.
- Advanced techniques: envelope tracking, supply modulation, DPD, harmonic
  tuning, Doherty/outphasing, or why they are unnecessary/out of scope.

## Runnable Backend Gate

Do not describe a topology as fully runnable unless all are true:

- The selected backend has a config, netlist/template, model binding, and spec
  parser entry for the topology.
- OP, S-parameter/stability, large-signal Pout/gain/PAE, harmonics,
  compression/AM-AM/AM-PM, and reliability checks are either implemented or
  explicitly marked out of scope for that topology.
- A smoke test has run and produced parseable results for the active metrics.
- The design review records the backend paths, simulation status, parser sanity
  status, and any metrics that remain advisory.

## Reference Loading Guide

- For beginner-safe feasibility and passive/reference-plane scoping, read
  `general/flow/student-preflight.md`.
- For spec parsing and declared assumptions, read `general/flow/spec-understanding.md`.
- For source-backed coverage expectations, read `general/reference/source-map.md`.
- For topology/class identification, read `general/flow/topology-understanding.md`.
- For equations, read `general/reference/pa-metrics.md`.
- For choosing amplifier class, read `general/reference/pa-classes.md`.
- For `PA_class = auto`, read `general/reference/class-auto-selection.md`.
- After class selection, read the matching
  `circuit-specific/<selected-topology>/*-design-flow.md`.
- For load-pull or matching work, read `general/reference/matching-and-load-pull.md`.
- For S-parameter stability or neutralization, read `general/reference/stability-neutralization.md`.
- For failed simulations, read `general/reference/root-cause-diagnosis.md`.
- For final reporting, read `general/flow/design-review.md`.
- For process-specific limits, read a matching `process/<process>.md` profile
  only when the task specifies that process.
- For local simulator paths/templates/API names, read a matching
  `backends/<backend>.md` adapter only when that backend is being used.
- For backend runnable status, read `backends/runnable-coverage-contract.md`
  and run `scripts/check_backend_coverage.py` when paths are available.
- For backend smoke tests, run `scripts/smoke_test_backend.py` when the selected
  backend API is reachable.
