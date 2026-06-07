# Differential Cascode Transformer RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Differential Output And Transformer Ratio

Define the differential load and transformer reference plane:

```text
Pout_total = Vdiff_pk^2 / (2 * Rdiff_load)
Rprimary_diff / Rsecondary ~= N^2
Rhalf_primary ~= Rprimary_diff / 2
```

Include winding resistance, coupling factor, and finite-Q loss before claiming
delivered Pout or PAE.

## Cascode Voltage Sharing

For each half-circuit:

```text
Vds_common_source_pk + Vds_cascode_pk = Vhalf_drain_pk
max(Vds_each_device) <= active device stress limit
```

Bias the cascode so transient waveform stress is shared safely. DC equality is
not sufficient.

## Neutralization

For differential common-source feedback:

```text
Cn_start ~= Cgd_eff
```

Sweep around this value and verify:

```text
S12 reduced
K or mu improved across frequency span
gain/bandwidth not over-degraded
AM/PM not worsened beyond target
```

Mismatch in transformer windings or neutralization capacitors can leave
residual positive feedback.

