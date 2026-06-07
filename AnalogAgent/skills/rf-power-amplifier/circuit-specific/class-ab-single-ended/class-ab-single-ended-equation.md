# Class-AB Single-Ended RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Bias Region

Class AB conduction angle is between Class A and Class B. The first-pass bias is
bounded by:

```text
0 < Idq < Ipk_device
theta_conduction between pi and 2*pi radians
```

The exact conduction angle must come from transient waveform current, not from
DC bias alone.

## First-Pass Current And Load

Use an efficiency bracket rather than a single assumed value:

```text
0.5 < eta_ideal_limit < 0.785
Pdc_required = Pout_target / eta_guess
Idc_total = Pdc_required / VDD
Rdev_ideal = Vpk_device^2 / (2 * Pout_target)
```

Choose `eta_guess` conservatively and update it after simulation.

## Drive And Gain

```text
Pin_available = Pout_target / gain_power_target
Vin_rms_source = sqrt(Pin_available * Rsource)
Av_required ~= Vpk_device / Vin_pk_available
gm_min ~= Av_required / Rload_eff
```

If the required gate swing exceeds the linear input range or compresses the
stage before nominal Pout, reduce drive, add a driver/final split, or resize.

## Compression And AM/AM

Run a power sweep. Compute:

```text
gain_db(Pin) = Pout_dbm(Pin) - Pin_dbm
P1dB where gain_db = gain_small_signal_db - 1
AMAM_nominal = gain_db(Pin_nominal) - gain_small_signal_db
AMPM_nominal = phase_out(Pin_nominal) - phase_out(low_drive)
```

Do not accept nominal Pout if it is already beyond the active compression
target.

