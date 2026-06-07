# Class-B Differential RF PA Design Flow

Use after topology understanding selects a differential or push-pull Class-B PA.

## Backend Mapping

- Required backend support: differential drive, differential load or combiner,
  branch current/stress reporting, OP, stability, large-signal, harmonic,
  compression, and load-mismatch analyses.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; scaffold-only until a differential testbench and
  combiner model exist in the selected backend.

## When To Use

- Efficiency is more important than Class-A linearity.
- A differential RF path, balun, transformer, or combiner is in scope.
- Even-order cancellation is useful and can be validated.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md`,
   `class-b-differential-equation.md`, and `general/reference/pa-metrics.md`.
2. Compute each half-circuit current and voltage stress in Python.
3. Size matched output devices for half the differential current each.
4. Model splitter and combiner losses; do not assume ideal conversion in final results.
5. Verify differential drive balance, common-mode node behavior, and even-order cancellation.
6. Run large-signal, harmonic, stability, P1dB, AM/AM, AM/PM, and load-mismatch checks with a differential-aware testbench.
7. If differential infrastructure is not modeled, keep the candidate as `defer`.

## Class-Specific Risks

- Ideal balun/combiner assumptions can overstate Pout and efficiency.
- Crossover distortion can dominate linearity.
- Current in each branch may pass while combined pad or load current fails.
