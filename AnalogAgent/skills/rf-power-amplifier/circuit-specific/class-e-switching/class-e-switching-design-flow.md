# Class-E Switching RF PA Design Flow

Use after topology understanding selects a Class-E switch-mode PA.

## Backend Mapping

- Required backend support: switch-mode transient RF analysis, waveform-stress
  extraction, finite-Q choke/load network modeling, harmonic analysis, and load
  mismatch.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; scaffold-only until switch waveform stress checks
  exist in the selected backend.

## When To Use

- Constant-envelope operation is acceptable.
- Efficiency dominates linearity.
- Harmonic waveform shaping and finite-Q passives are in scope.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md`,
   `class-e-switching-equation.md`, `general/reference/pa-metrics.md`, and
   `general/reference/matching-and-load-pull.md`.
2. Compute switch peak voltage, peak current, shunt capacitance, and load network values in Python.
3. Include device output capacitance as part of the Class-E shunt capacitance.
4. Add finite-Q loss for choke, series network, and shunt capacitance ESR where available.
5. Verify zero-voltage or low-voltage switching behavior, peak Vds, peak current, Pout, efficiency, harmonics, and load mismatch.
6. Reject if peak device voltage exceeds the active process/device reliability
   limit.

## Class-Specific Risks

- Ideal Class-E waveforms can exceed low-voltage device limits.
- Finite-Q passives can erase expected efficiency gains.
- On-chip low-RF inductors may be too large or too lossy for ideal synthesis.
