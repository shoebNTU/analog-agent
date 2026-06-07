# RF PA Equation Framework

Use this shared framework before reading a topology-specific equation file.
All calculations must be executed in Python.

## Signal And Power Conventions

Declare the reference plane before using any equation:

```text
Pout_delivered = power delivered to the specified load/reference plane
Pin_available  = available input power at the specified input reference plane
Vpk_load       = peak sinusoidal voltage across the specified real load
Ipk_load       = peak sinusoidal current through the specified real load
```

For a real sinusoidal load:

```text
Pout = Vpk_load^2 / (2 * Rload)
Vpk_load = sqrt(2 * Pout * Rload)
Vrms_load = sqrt(Pout * Rload)
Ipk_load = Vpk_load / Rload
Irms_load = Vrms_load / Rload
```

For a target device load:

```text
Rdev_ideal = Vpk_device^2 / (2 * Pout_device)
transform_ratio = R_reference / Rdev_ideal
```

Use delivered simulator power as source of truth after simulation.

## Efficiency

```text
Pdc = sum(Vsupply_i * Idc_i)
drain_efficiency = Pout_delivered / Pdc
PAE = (Pout_delivered - Pin_available) / Pdc
gain_power = Pout_delivered / Pin_available
```

Include driver and bias-network power in Pdc when those blocks are part of the
active design boundary. Include matching loss before claiming delivered Pout.

## Device And Transconductance First Pass

For voltage-mode common-source sizing:

```text
Av_est ~= gm * Rload_eff
gm_min ~= gain_voltage_target / Rload_eff
Id_est ~= gm_min / gm_over_id_target
```

For current-limited output sizing:

```text
Ipk_device >= Vpk_device / Rdev_ideal
Idc_total <= active_current_limit
```

Derive final device width from the active process model, LUT, or backend
parameter map. Do not use a universal current density.

## Matching And Q

For a first-pass L-match between `R_high` and `R_low`:

```text
Q_loaded = sqrt(R_high / R_low - 1)
X_series = Q_loaded * R_low
X_shunt = R_high / Q_loaded
L = X / (2*pi*f0)
C = 1 / (2*pi*f0*X)
```

Absorb device capacitances into the matching network when possible. Recompute
component currents, voltage stress, finite-Q loss, and bandwidth.

## Reliability

Check at least:

```text
max_abs_vds <= Max_device_voltage - margin
abs(Idc_total) <= Max_Idc_total
Iout_rms <= Max_output_current_rms
Iout_pk <= Max_output_current_pk
```

For switch-mode and tuned classes, peak drain voltage can be much larger than
VDD. Use transient waveform stress, not only DC OP.

## Stability

Use S-parameter metrics when available:

```text
Delta = S11*S22 - S12*S21
K = (1 - |S11|^2 - |S22|^2 + |Delta|^2) / (2*|S12*S21|)
mu = (1 - |S11|^2) / (|S22 - Delta*conj(S11)| + |S12*S21|)
```

Require `K > 1` and `|Delta| < 1`, or `mu > 1`, only when those criteria match
the backend port definitions and the requested stability scope. Always report
the frequency span.

