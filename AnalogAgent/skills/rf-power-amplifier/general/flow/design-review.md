# RF PA Design Review

## Purpose

Summarize the final RF PA state after success, timeout, or infeasibility.

## Rules

1. Use the exact section order below.
2. Fill every `<...>` field. If unavailable, write `--` and explain why in
   Section 6.
3. Recompute first-pass metrics from the final sizing in Python before printing.
4. Separate active failures from advisory/system-level residual risks.
5. Do not claim signoff without layout parasitics/EM extraction and required
   large-signal verification across PVT, temperature, and load mismatch.
6. If S11/S22 are poor but advisory, include the match-closure contract from
   `general/reference/matching-and-load-pull.md`; do not leave return loss as an
   unexplained caveat.
7. Include a source-backed coverage table from
   `general/reference/source-map.md`; every source topic must be active,
   advisory, out_of_scope, or missing.

## Step 0 - Maintain Iteration Log

Every simulation iteration should append one row:

```python
stability_vals = [
    specs.get("stability_k"),
    specs.get("stability_mu"),
]
stability_vals = [v for v in stability_vals if v is not None]
iteration_log.append({
    "iter": N,
    "change": "<one-line change>",
    "pout_dbm": specs.get("pout_dbm"),
    "gain_db": specs.get("gain_db"),
    "pae": specs.get("pae"),
    "stability": min(stability_vals) if stability_vals else None,
    "decision": "pass" or "fail: <which specs>",
})
```

## Step 1 - Recompute Final First-Pass Metrics

Before printing the report, recompute final target load, voltage/current swing,
Pdc, ideal efficiency estimate, and matching values from the final sizing.
Print/store this dict as `first_pass_final`.

## Step 2 - Print Report

```text
==========================================================
RF PA DESIGN REVIEW
==========================================================

1. OUTCOME
----------
STATUS: <SUCCESS / TIMEOUT / INFEASIBLE>

2. SPECIFICATION COMPLIANCE
----------------------------
Spec          | Target      | Class      | First-pass | Simulated | Margin | Status
Pout          | <>          | <>         | <>         | <>        | <>     | <>
Gain          | <>          | <>         | <>         | <>        | <>     | <>
PAE           | <>          | <>         | <>         | <>        | <>     | <>
Drain eff.    | <>          | <>         | <>         | <>        | <>     | <>
Linearity     | <>          | <>         | <>         | <>        | <>     | <>
Stability     | <>          | <>         | <>         | <>        | <>     | <>
Reliability   | <>          | <>         | <>         | <>        | <>     | <>

Advisory / residual:
  S11/S22       : <>
  Load mismatch : <>
  P1dB/AM-AM/PM : <>
  Bias network  : <>
  Large passives: <>
  Parser sanity : <>
  Match closure : <>
  EM/layout     : <>
  Package/pads  : <>

3. SIZING AND MATCHING SUMMARY
-------------------------------
Topology      : <>
PA class      : <>
Process       : <>
f0            : <>
VDD           : <>
R_load ext.   : <>
R_load device : <>

Device/Block  | W/L/M or value | Bias/current | RF swing/stress | Purpose
<>            | <>             | <>           | <>              | <>

Backend:
  Name         : <>
  Config       : <>
  Template     : <>
  Status       : runnable_seed / scaffold_only / custom

Matching network:
  Input       : <>
  Interstage  : <>
  Output      : <>
  Reference plane now    : <>
  Reference plane target : <>
  S11/S22 activation     : active / advisory / residual, because <>
  Match-closure contract : missing model/scope=<>, template/API knobs=<>,
                           bounded schematic attempt=<>, activation sims=<>

4. SIMULATION SETUP
--------------------
Analysis      | Settings
DC/OP         | <>
S-parameter   | <>
Large-signal  | <>
Load-pull     | <>
Linearity     | <>
EM/layout     | <>

5. ITERATION HISTORY
---------------------
Iter | Change Made | Pout(dBm) | Gain(dB) | PAE(%) | Stability | Decision
1    | <>          | <>        | <>       | <>     | <>        | <>

6. RESIDUAL RISKS
------------------
- <>

7. SOURCE-BACKED COVERAGE
--------------------------
Topic                 | State       | Evidence / reason
Efficiency            | <>          | <>
Nonlinearity          | <>          | <>
Amplifier class       | <>          | <>
Matching/load-pull    | <>          | <>
Stability/neutral.    | <>          | <>
Reliability           | <>          | <>
Advanced techniques   | <>          | <>
Implementation closure| <>          | <>
```

## Validation Checklist

- Section 2 marks each spec as active/advisory/residual in the `Class` column.
- Section 3 identifies the backend and config/template used, or says no
  simulator backend was used.
- Section 5 has one row per actual iteration.
- Section 6 includes every unmodeled risk, especially EM/layout and package/pad
  effects when not simulated.
- Section 2 or Section 6 explicitly states whether S-parameter parser/raw-file
  sanity was verified before trusting S11/S22/K/mu.
- If S11/S22 are advisory and worse than target, Section 3 contains a
  match-closure contract with missing model/scope, needed template/API knobs,
  bounded schematic attempts, and activation simulations.
- Section 6 explicitly calls out ideal bias sources, large inductors/traps,
  load-mismatch current, and compression if any remain unresolved.
- Section 7 has no `missing` rows unless the report status is TIMEOUT or
  INFEASIBLE and the missing coverage is named as a blocker.
