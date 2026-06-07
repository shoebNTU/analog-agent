# Class-B Differential RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Differential Power Split

Define whether the load is differential or each half-circuit sees a transformed
single-ended load:

```text
Pout_total = Pout_plus_half + Pout_minus_half
Pout_half = Pout_total / 2
```

For a differential load `Rdiff`:

```text
Pout_total = Vdiff_pk^2 / (2 * Rdiff)
Vhalf_pk = Vdiff_pk / 2
```

## Class-B Current

For ideal sinusoidal Class B operation:

```text
theta_conduction = pi radians
Ipk_half = Vhalf_pk / Rhalf_eff
Idc_half_ideal = Ipk_half / pi
Pdc_total = 2 * VDD * Idc_half_ideal
eta_ideal <= pi / 4
```

Use this only as a first-pass bound; crossover distortion and finite device
headroom reduce performance.

## Even-Order Cancellation

Differential symmetry ideally cancels even-order output components. In
simulation, verify:

```text
H2_diff_dBc <= target
common_mode_swing within bias/stress limits
branch_current_plus ~= branch_current_minus
```

Mismatch, transformer imbalance, and asymmetric layout can break cancellation.

