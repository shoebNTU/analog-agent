# Two-Stage Single-Ended RF PA Design Flow

Use when the topology is a driver stage feeding a larger single-ended output
stage. This corresponds to the textbook's two-stage PA archetype.

## Backend Mapping

- Required backend support: driver and output-stage devices, interstage network
  modeling, RF source/load, OP, S-parameter, large-signal, harmonic, power
  sweep, compression, and stability analyses.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; scaffold-only until the selected backend provides
  both-stage simulation support.

## When To Use

- The final output transistor requires more drive than the source can provide.
- The requested gain cannot be met by a single final stage.
- The final device gate capacitance would over-load the RF source or previous block.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md` and
   `two-stage-single-ended-equation.md`; run `general/flow/student-preflight.md`
   for output-stage feasibility.
2. Size the output stage first from Pout, load, voltage/current stress, and class.
3. Estimate the output device required input voltage/current drive and input capacitance.
4. Size the driver to deliver that drive with margin while staying linear enough for the target modulation.
5. Add an interstage match or damping network; do not assume the driver sees a benign load.
6. Verify reverse coupling and stability across both stages. Extra gain can create oscillation risk.
7. Simulate Pout, gain, PAE, P1dB, AM/AM, AM/PM, harmonics, and transient stress with both stages present.
8. If active core metrics pass but final S11/S22 are poor, follow the
   return-loss closure contract in `general/reference/matching-and-load-pull.md`.
   Optimize modeled input/output damping or L/C values only within bounded
   sweeps that preserve stability, current limits, compression, harmonics, Pout,
   gain, and PAE. Do not claim package/board reference-plane closure unless that
   reference plane is modeled.

## Class-Specific Risks

- Driver power reduces PAE and can dominate low-power designs.
- Interstage matching can narrow bandwidth and create unintended resonances.
- A stable final stage can become unstable once the driver and interstage match are added.
- Improving S11/S22 by adding damping or retuning interstage/output networks can
  reduce gain/PAE or disturb harmonic traps; re-run the full active metric set.
