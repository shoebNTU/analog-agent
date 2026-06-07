# Class-C Tuned RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Conduction Angle

Class C conducts for less than half the RF cycle:

```text
theta_conduction < pi radians
```

The conduction angle must be measured from drain current waveform threshold
crossings in transient or harmonic-balance simulation.

## Tuned Load Requirement

The output tank or match must recover the fundamental component from a pulsed
current waveform:

```text
Pout_fundamental = Vrms_fundamental^2 / Rload
Q_loaded = f0 / bandwidth
```

High Q improves selectivity but worsens bandwidth, tolerance sensitivity, and
current stress.

## Current Pulse Stress

Do not size from average DC current alone:

```text
Ipk_device >= max(i_drain_waveform)
Idc = average(i_drain_waveform)
eta = Pout_fundamental / (VDD * Idc)
```

Peak current and peak voltage are active reliability checks.

## Applicability

Use Class C only when modulation permits nonlinear amplitude behavior or when a
linearization/system technique is explicitly in scope.

