# Example: GF180MCU-D 250 MHz, 2 mW RF PA

This is a non-binding example spec. Use it only when the user explicitly asks
for this example or provides the same targets.

```text
Design_scope   : on_chip_core_only
Process        : GF180MCU-D
f0             : 250e6
VDD            : 3.3
Pout_target    : 2e-3
R_load         : 50
PA_class       : auto
f_max_pad      : 300e6
I_pad_max      : 10e-3
Max_Idc_total  : 10e-3
Max_output_current_rms : 10e-3
Max_output_current_pk  : 10e-3
Max_device_voltage     : 3.3
Reference_plane: schematic_output_node
Passive_scope  : schematic_available_only
Passive_model_level : finite_Q_lumped
```

Rationale: the output target is intentionally conservative for a pad-current
limited example. It should not be treated as the default RF PA target.
