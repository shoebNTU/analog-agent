# Class-A Single-Ended RF PA Design Flow

Use after topology understanding selects a single-ended Class-A PA.

## Backend Mapping

- Required backend support: single-ended common-source PA with bias, finite-Q
  output network, RF source/load, OP, S-parameter, large-signal, harmonic, and
  compression analyses.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; scaffold-only until the selected backend marks the
  implementation runnable.

## When To Use

- Linearity is more important than drain efficiency.
- Output power is modest enough for the current and voltage limits.
- Constant 360-degree conduction is acceptable for the power budget.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md`,
   `class-a-single-ended-equation.md`, and `general/reference/pa-metrics.md`.
2. Compute target device load, voltage swing, current swing, and DC power in Python.
3. Bias the device near mid-conduction; keep `Idc_total` below the active limit.
4. Size the common-source device from required gm and current density.
5. Synthesize the output match or tuned load, then include finite-Q series loss.
6. Verify DC current, Pout, gain, drain efficiency, PAE, H2/H3, S-parameter stability, P1dB, AM/AM, and AM/PM.
7. If efficiency fails, do not force Class A; rank Class AB/B as alternatives.

## Class-Specific Risks

- Usually poor efficiency under tight current or power limits.
- Excess static current can violate pad or power budget before Pout is met.
- Large on-chip inductors may dominate loss at low RF frequencies.
