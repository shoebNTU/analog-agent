# Class-A Single-Ended RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Bias And Swing

Class A conducts for the full RF cycle. Bias the output device so the expected
RF current and voltage swings remain inside the active current and voltage
limits:

```text
Idq >= Ipk_device
Vdq margin supports +/- Vpk_device swing
Pdc = VDD * Idq
```

For an ideal transformer or tuned load at the drain:

```text
Rdev = Vpk_device^2 / (2 * Pout_device)
Ipk_device = Vpk_device / Rdev
```

## Efficiency Bound

Use the ideal Class-A drain-efficiency ceiling only as a sanity bound:

```text
eta_drain <= 0.5
Pdc_required >= Pout_target / eta_drain_target
```

If the design uses resistive load or large quiescent margin, expect lower
efficiency.

## Gain And Width

```text
Av_est ~= gm * Rload_eff
gm_min = Av_target / Rload_eff
Idq = gm_min / gm_over_id_target
```

Derive width from the process LUT or model at the selected bias point. Recheck
output capacitance because it becomes part of the RF load/match.

## Required Checks

- `Idq`, `Pdc`, and thermal budget.
- Output swing headroom and peak terminal stress.
- Gain, Pout, PAE, and harmonic levels.
- S-parameter stability across the required span.
- Compression even if Class A is expected to be linear.

