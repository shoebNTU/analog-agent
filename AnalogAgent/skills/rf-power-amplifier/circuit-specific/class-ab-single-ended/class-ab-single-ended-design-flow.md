# Class-AB Single-Ended RF PA Design Flow

Use after topology understanding selects a single-ended Class-AB PA.

## Backend Mapping

- Required backend support: single-ended common-source PA with controllable
  gate bias, finite-Q matching, RF source/load, OP, S-parameter, large-signal,
  harmonic, power-sweep, and load-mismatch analyses.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; use simulated evidence only after the selected
  backend marks the implementation runnable.

## When To Use

- This is the default linear RF PA starting point.
- Linearity matters, but Class-A current is too expensive.
- Modest compression and AM/AM or AM/PM checks are active.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md`,
   `class-ab-single-ended-equation.md`, `general/reference/pa-metrics.md`, and
   `general/reference/matching-and-load-pull.md`.
2. Compute target transformed load, voltage swing, current swing, and DC power in Python.
3. Pick quiescent current from the current limit and expected conduction angle.
4. Size the common-source output device from current, gm, and available drive.
5. Add gate damping and bias resistance; re-check gain and stability.
6. Synthesize the output match with finite-Q passives and include harmonic traps only when their loss and current are modeled.
7. Before accepting nominal Pout/gain/PAE, run RFPA simulation for DC, large signal, S-parameter estimate, harmonics, power sweep, and load mismatch.
8. If S11/S22/K/mu fail, stabilize and rematch before optimizing power.
9. If nominal Pin is already compressed, back off drive, increase headroom, or resize/rebias; do not report nominal Pout as a clean operating point.
10. If load mismatch exceeds current/voltage limits, redesign the fundamental match and harmonic traps using load-pull contours.
11. If Pout or efficiency fails after stability, compression, and mismatch are under control, iterate load, bias, width, and finite-Q passives before changing class.

## Class-Specific Risks

- Too much bias becomes Class-A-like and wastes current.
- Too little bias produces crossover distortion and poor AM/AM.
- Output match and harmonic traps can improve waveforms but worsen load mismatch current.
- A design that meets nominal Pout/gain/PAE can still be unusable if K/mu,
  return loss, P1dB, AM/AM, AM/PM, or VSWR current fail.
- Ideal drain-bias current sources hide RF-choke/PMOS bias capacitance,
  headroom, and efficiency penalties. Replace them before final review.
