# GF180MCU-D RF PA Process Profile

Use this file only when the active task names GF180MCU-D or uses a local
GF180MCU-D simulator configuration. This profile is not part of the generic RF
PA defaults.

## Device And Reliability Context

- Nominal low-voltage supply often used in this workspace: `VDD = 3.3 V`.
- Available MOS devices in the local GF180MCU-D setup: `nfet_03v3`,
  `pfet_03v3`.
- Minimum channel length in the local setup: `0.28 um`.
- Common process corners in the local setup: `typical`, `ff`, `ss`, `fs`, `sf`.
- Treat terminal stress, current density, passive limits, and pad/package
  constraints as design inputs. Do not assume a value is active unless it is in
  the user's spec, PDK documentation, or simulator configuration.

## Local Workspace Example Limits

The values below came from one pad-limited example and are examples only:

- `f0 = 250e6`
- `f_max_pad = 300e6`
- `Pout_target = 2e-3 W`
- `R_load = 50 ohm`
- `I_pad_max = 10e-3 A`
- `Max_device_voltage = 3.3 V`

Never copy these into a new design unless the user explicitly selects this
example or provides equivalent requirements.

## Process Binding Output

When this process profile is used, print:

```text
RF PA PROCESS PROFILE
=====================
Process       : GF180MCU-D
Devices       : <devices used or unknown>
Supply        : <from user spec or simulator config>
Corners       : <from user spec or simulator config>
Hard limits   : <source of each voltage/current/frequency limit>
Example values: inactive unless explicitly selected
```

