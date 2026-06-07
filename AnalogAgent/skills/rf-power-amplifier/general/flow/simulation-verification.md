# RF PA Simulation Verification

## Purpose

After the selected class-specific flow produces a sizing and simulation run,
verify active specs, classify advisory/system-level risks, and decide whether
to iterate, stop, or proceed to review.

## Required Simulation Checks

Use the simulator capabilities available in the workspace. Prefer harmonic
balance/load-pull if available; otherwise use transient periodic steady-state
style runs and FFT/power extraction.

## Step 1 - DC and Reliability

Check every active device:

```
Device | Id(avg) | Vds(dc) | Vgs(dc) | max|Vds(t)| | max|Vgs(t)| | Limit | Status
```

Flag failure before performance tuning if voltage/current stress exceeds PDK
limits or if cascode sharing is poor.

## Step 2 - Small-Signal RF Stability

At minimum, evaluate S-parameters around and beyond `f0`:

```
Freq span: f0/10 to 10*f0 unless a wider risk band is specified.
Check: K > 1 and |Delta| < 1, or mu > 1, plus no suspicious input/output
negative resistance with intended terminations.
```

If neutralization is present, sweep neutralization cap mismatch.

For `Design_scope = on_chip_core_only`, final external S11/S22 may be advisory
when pads, package, ESD, and off-chip matching are not modeled. Core instability
or negative resistance remains an active failure.

### S-Parameter Parser Sanity Check

Before using S11/S22/K/mu for optimization, verify the parser against the raw
simulator output at the frequency nearest `f0`.

Mandatory checks:

- Confirm the `wrdata` column order, especially for ngspice complex outputs
  that duplicate frequency columns.
- Recompute S11/S22/K/mu from the raw file for one point near `f0`.
- If API-reported values disagree with the raw-file recomputation, stop and
  fix the parser before optimizing the circuit.
- Even if parser correction improves the numbers, keep the design failed when
  corrected S11/S22/K/mu miss their active limits.

## Step 3 - Large-Signal Metrics

Report:

- `Pout` delivered to the external load.
- `Pin` available from source.
- Transducer/power gain.
- DC power.
- Drain efficiency.
- PAE.
- P1dB or compression relative to small-signal gain.
- AM/AM and AM/PM over input drive.
- Harmonic powers and waveform clipping/stress.
- Load-pull or source-pull result if performed.

Use `general/reference/pa-metrics.md` for conversions.

## Step 4 - Active vs Advisory Classification

Before the compliance table, classify each metric:

```
RF PA METRIC CLASSIFICATION - Iteration <N>
===========================================
Metric        | Active/advisory/residual | Reason
Pout          | active                   | <why>
S11/S22       | active/advisory          | <modeled scope>
Load mismatch | active/advisory          | <modeled scope>
EM/layout     | residual                 | <layout not available / extracted>
```

Only active metrics can fail the design loop. Advisory and residual metrics
must be reported in the design review, but they do not block an on-chip-core
schematic iteration unless the needed external elements are modeled.

### Return-Loss Closure Decision

After classifying S11/S22, make one of these decisions:

```text
active_match_failed:
  S11/S22 target applies at a modeled reference plane and the result misses it.
  -> run root-cause diagnosis, synthesize/optimize the modeled input/output
     match, and re-simulate before SUCCESS.

advisory_match_gap:
  S11/S22 is poor, but package/off-chip/pad/EM or final external reference-plane
  elements are absent.
  -> do not fail the core solely for return loss; write a match-closure
     contract in the review and list required backend/template/API model
     features to make S11/S22 active.

bounded_schematic_improvement:
  Schematic-only match/damping knobs exist and can be swept without pretending
  to close package/board return loss.
  -> try a bounded sweep only if it does not degrade active Pout/gain/PAE,
     reliability, stability, P1dB, or harmonics; otherwise keep the advisory
     caveat and closure contract.
```

## Step 5 - Compliance Table

```
RF PA SPEC COMPLIANCE - Iteration <N>
=====================================
Spec          | Target      | Achieved    | Margin | Status
Pout          | > <dBm>     | <dBm>       | <>     | pass/fail
Gain          | > <dB>      | <dB>        | <>     | pass/fail
PAE           | > <%>       | <%>         | <>     | pass/fail
Drain eff.    | > <%>       | <%>         | <>     | pass/fail
Stability     | K/mu        | min <val>   | <>     | pass/fail
Reliability   | limits      | worst <val> | <>     | pass/fail
Linearity     | <metric>    | <val>       | <>     | pass/fail
```

Include only active specs in the pass/fail count. Report advisory metrics
below the table.

## Step 6 - Analytical vs Simulated Check

Compare first-pass calculations from the selected class-specific flow against
simulation. Use Python-computed values only.

```
RF PA FIRST-PASS vs SIMULATION - Iteration <N>
==============================================
Metric        | First-pass | Simulated | Error | Interpretation
Pout          | <>         | <>        | <>    | <>
Idc/Pdc       | <>         | <>        | <>    | <>
Efficiency    | <>         | <>        | <>    | <>
Load/current  | <>         | <>        | <>    | <>
```

Large discrepancy means the model or matching assumptions need repair before
blindly resizing devices.

## Step 7 - Decision Logic

Track `iteration_count` across simulation loops.

```
MAX_ITERATIONS = 8

IF any hard reliability failure:
  -> CRITICAL failure; proceed to root-cause diagnosis.

ELIF active stability fails:
  -> Stability failure; proceed to root-cause diagnosis.

ELIF load mismatch creates current/voltage overstress:
  -> Ruggedness failure; proceed to root-cause diagnosis.

ELIF active S11/S22 target fails at the modeled reference plane:
  -> Match failure; proceed to root-cause diagnosis.

ELIF nominal Pin is already beyond P1dB or AM/AM/AM/PM limits:
  -> Compression/linearity failure; proceed to root-cause diagnosis.

ELIF all active specs PASS:
  -> PASSED; proceed to design-review.md. If advisory S11/S22 are poor, include
     the match-closure contract instead of treating it as a silent pass.

ELIF iteration_count >= MAX_ITERATIONS:
  -> TIMEOUT; proceed to design-review.md and report best achieved result.

ELSE:
  -> Spec failure; proceed to root-cause diagnosis.
```

Do not let Pout, gain, or PAE improvements override reliability failures.

## Step 8 - Iteration Summary

Before entering diagnosis or review, print:

```
RF PA ITERATION <N> SUMMARY
===========================
Status   : PASSED / FAILED / TIMEOUT
Active   : <M>/<N> active specs met
Critical : <reliability/stability issues or none>
Advisory : <S11/S22/load mismatch/EM notes>
Match    : <active_match_failed / advisory_match_gap / bounded_schematic_improvement / closed>
Next     : <design-review.md / root-cause-diagnosis.md>
```

## Next Stage

- If PASSED -> `general/flow/design-review.md`
- If FAILED -> `general/reference/root-cause-diagnosis.md`
- If TIMEOUT -> `general/flow/design-review.md`
