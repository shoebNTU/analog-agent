# Class-E Switching RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Ideal Class-E Starting Point

Class E is switch-mode and relies on waveform shaping. Ideal normalized
relationships are first-pass seeds only:

```text
Rload_opt ~= 0.577 * VDD^2 / Pout_target
Cshunt_ideal ~= 0.1836 / (omega0 * Rload_opt)
Lseries_ideal ~= 1.1525 * Rload_opt / omega0
```

`Cshunt_ideal` includes device output capacitance, package capacitance, and any
explicit shunt capacitor:

```text
Cshunt_external = Cshunt_ideal - Coss_device - Cparasitic
```

If this value is negative, the target/load/frequency is incompatible with the
device capacitance without changing the network.

## Waveform Conditions

Verify in transient or harmonic-balance simulation:

```text
Vds(turn_on) ~= 0
dVds_dt(turn_on) ~= 0
max(Vds) <= active device stress limit
max(Ids) <= active current limit
```

The ideal peak drain voltage can exceed VDD by a large factor, so voltage stress
is the first acceptance gate.

## Loss Budget

Include finite Q and switch loss:

```text
P_loss = P_switch_on + P_cap_esr + P_inductor_esr + P_match_loss
eta = Pout / (Pout + P_loss + Pdc_control_losses)
```

Do not claim high efficiency from ideal passive equations alone.

