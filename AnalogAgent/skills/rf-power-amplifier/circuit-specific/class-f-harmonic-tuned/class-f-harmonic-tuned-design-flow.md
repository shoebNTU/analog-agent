# Class-F Harmonic-Tuned RF PA Design Flow

Use after topology understanding selects a Class-F or inverse-Class-F PA.

## Backend Mapping

- Required backend support: fundamental and harmonic termination modeling,
  finite-Q passives, waveform-stress extraction, large-signal, harmonic,
  stability, and load-mismatch analyses.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; scaffold-only until harmonic termination checks
  exist in the selected backend.

## When To Use

- Efficiency is the primary goal.
- Harmonic terminations are explicitly modeled.
- The design can tolerate narrowband tuning and waveform-shaping risk.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md`,
   `class-f-harmonic-tuned-equation.md`, `general/reference/pa-metrics.md`, and
   `general/reference/matching-and-load-pull.md`.
2. Compute fundamental load and harmonic target impedances in Python.
3. Choose harmonic termination strategy: open/short at 2f0/3f0 or inverse-Class-F alternative.
4. Include finite-Q loss and parasitic detuning in every harmonic network.
5. Verify drain waveform shape, peak Vds, peak current, Pout, efficiency, H2/H3, stability, and load mismatch.
6. Reject if harmonic networks are unmodeled or if voltage stress cannot be kept inside limits.

## Class-Specific Risks

- Correct harmonic impedance matters more than small-signal gain.
- Harmonic traps can improve one metric while worsening load current or stability.
- Layout and passive parasitics can invalidate schematic harmonic tuning.
