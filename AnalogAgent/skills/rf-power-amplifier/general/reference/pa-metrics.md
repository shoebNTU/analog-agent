# PA Metrics and Equations

Use Python for every calculation.

## Power Conversions

```python
import math
def w_to_dbm(p_w): return 10 * math.log10(p_w / 1e-3)
def dbm_to_w(p_dbm): return 1e-3 * 10**(p_dbm / 10)
def db_to_lin(x_db): return 10**(x_db / 10)
def lin_to_db(x): return 10 * math.log10(x)
```

## Output Power and Load

For a sinusoidal voltage swing with peak amplitude `Vpk` across a real load:

```text
Pout = Vpk^2 / (2 * Rload)
Vpk  = sqrt(2 * Pout * Rload)
Ipk  = Vpk / Rload
```

For an ideal voltage-limited single-ended PA:

```text
Pout_max ~= VDD^2 / (2 * R_device)
R_device ~= VDD^2 / (2 * Pout_target)
```

For differential outputs, define clearly whether `Vpk` is single-ended or
differential. Use the simulator's delivered load power as source of truth.

## Efficiency

```text
Pdc = VDD * Idc_total
drain_efficiency = Pout / Pdc
PAE = (Pout - Pin) / Pdc
power_gain = Pout / Pin
```

PAE is the better metric when input drive is large.

Always state whether the reported Pout is delivered at the load/reference plane
or available at an internal device plane. Include finite-Q matching loss,
transformer loss, driver power, and bias-network current when those are known.
If they are unknown, mark efficiency and PAE as optimistic.

## Compression and AM/AM, AM/PM

Sweep input power:

- Small-signal gain: low-drive slope.
- P1dB: output power where gain is 1 dB below small-signal gain.
- AM/AM: output amplitude vs input amplitude.
- AM/PM: output phase shift vs input amplitude.

For a first behavioral model, the Saleh equations are a useful compact fit:

```text
A(r) = alpha1 * r / (1 + beta1 * r^2)
phi(r) = alpha2 * r^2 / (1 + beta2 * r^2)
```

Fit only to simulated or measured data; do not use as device physics.

For modulated signals, do not use single-tone P1dB alone as the linearity
closure. Carry PAPR, EVM, ACLR, IM3, spectral mask, or DPD assumptions from the
spec. If these are absent, state that the design is single-tone characterized
only.

## First-Pass Current

For a chosen class and approximate drain efficiency `eta_guess`:

```text
Pdc_required = Pout_target / eta_guess
Idc_total = Pdc_required / VDD
```

Typical optimistic first-pass `eta_guess`:

- Class A: <= 0.5
- Class B: <= 0.785
- Class AB: between Class A and B
- Class C/E/F: high, but waveform tuning and linearity dominate

## Reference-Backed Metric Checklist

Every PA review should classify each metric as `active`, `advisory`,
`out_of_scope`, or `missing`:

| Category | Metrics |
|---|---|
| Power | Pout, Pin, gain, Pdc, drain efficiency, PAE |
| Nonlinearity | P1dB/compression, AM/AM, AM/PM, PAPR, EVM/ACLR/IM3 if relevant |
| Spectral | H2, H3, spurs, spectral mask if relevant |
| Matching | Reference-plane S11/S22, device load, source/load-pull status |
| Stability | K, mu, Delta, out-of-band sweep, S12/Miller risk |
| Reliability | Peak/RMS current, device voltage stress, duty cycle/thermal notes |
