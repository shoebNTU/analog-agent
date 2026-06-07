# Class-C Tuned RF PA Design Flow

Use after topology understanding selects a tuned Class-C PA.

## Backend Mapping

- Required backend support: tuned load modeling, conduction-angle visibility,
  finite-Q passives, OP, large-signal, harmonic, waveform-stress, and
  load-mismatch analyses.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; scaffold-only until conduction-angle and
  tuned-load checks exist in the selected backend.

## When To Use

- The signal is constant-envelope or narrowband.
- Efficiency matters more than linearity.
- A tuned load is explicitly in scope.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md`,
   `class-c-tuned-equation.md`, `general/reference/pa-metrics.md`, and
   `general/reference/matching-and-load-pull.md`.
2. Compute required output energy, tank impedance, and current pulse stress in Python.
3. Bias below or near threshold to set conduction angle.
4. Size the device from peak current, not only average current.
5. Synthesize the tuned load and include finite-Q loss.
6. Verify startup/settling, Pout, efficiency, harmonics, peak device stress, and load mismatch.
7. Reject for high-PAPR or stringent linearity unless linearization is explicitly included.

## Class-Specific Risks

- P1dB and AM/AM are often unsuitable as primary linearity measures.
- Peak current can violate limits while average DC current looks safe.
- Narrowband tuned networks are sensitive to finite-Q and parasitics.
