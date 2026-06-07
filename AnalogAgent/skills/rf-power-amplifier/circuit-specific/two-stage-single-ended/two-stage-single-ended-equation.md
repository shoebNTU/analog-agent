# Two-Stage Single-Ended RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Stage Budgeting

Split the required power gain:

```text
G_total = Pout_target / Pin_available
G_total_db = G_driver_db + G_output_db - interstage_loss_db
```

The output stage is sized first from Pout, load, and stress. The driver is then
sized for the output stage input drive and capacitance.

## Output Stage

Use the class-specific equation file for the output device class. Compute:

```text
Rdev_output
Vpk_output
Ipk_output
Pin_required_output = Pout_target / G_output
```

## Driver Stage

Estimate output-stage input demand:

```text
Cin_output ~= Cgs_output + Cgd_output * (1 + abs(Av_output))
Ipk_gate_drive ~= omega0 * Cin_output * Vgate_pk_output
Pdrive_required >= Pin_required_output
```

The interstage network must be included in gain, bandwidth, stability, and PAE.

## PAE With Driver

```text
Pdc_total = Pdc_driver + Pdc_output + Pdc_bias
PAE_total = (Pout_delivered - Pin_available) / Pdc_total
```

Driver power can dominate low-power designs; never report output-stage-only PAE
as total PA PAE.

