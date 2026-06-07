# Differential Cascode Transformer RF PA Design Flow

Use when the topology is a differential cascode PA with transformer or balun
input/output matching. This corresponds to the textbook's high-isolation,
wideband differential PA archetype.

## Backend Mapping

- Required backend support: differential cascode devices, transformer/balun
  model, finite-Q winding loss, differential/common-mode stability, large-signal
  RF, harmonic, waveform-stress, and load-mismatch analyses.
- Local simulator mappings, if any, must come from the selected backend adapter
  such as `backends/circuitcollector.md`.
- Status: backend-dependent; scaffold-only until the selected backend provides
  the required differential and transformer models.

## When To Use

- Voltage stress or reverse isolation requires cascodes.
- Differential operation and transformer/balun matching are in scope.
- Neutralization or cross-coupled cancellation is needed for stability/bandwidth.

## Procedure

1. Read `general/reference/rfpa-equation-framework.md` and
   `differential-cascode-transformer-equation.md`; run
   `general/flow/student-preflight.md` and define whether the reference plane
   is differential load, transformer primary, transformer secondary, pad, board
   load, or custom.
2. Split output power, voltage swing, and current stress consistently between each half-circuit and the differential load.
3. Size the common-source devices for current and gm, then size cascodes for voltage sharing and isolation.
4. Model transformer turns ratio, coupling factor, winding resistance, and finite Q. Treat ideal transformers as first-pass only.
5. If neutralization is used, estimate required cancellation from Cgd/Miller feedback and sweep mismatch.
6. Verify K/mu or equivalent differential-mode/common-mode stability over a broad frequency range.
7. Simulate large-signal Pout, gain, PAE, AM/AM, AM/PM, harmonics, waveform stress, and load mismatch with the transformer model included.

## Class-Specific Risks

- Cascode bias errors can over-stress one device even when total VDD seems safe.
- Ideal transformers can badly overstate Pout, bandwidth, and PAE.
- Neutralization improves reverse isolation only when tuned; mismatch can leave residual positive feedback.
