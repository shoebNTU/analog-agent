# RF Power Amplifier On-Chip Core Spec Form

This is a generic on-chip-core form. It intentionally avoids process, frequency,
power, supply, and current defaults. Fill every active value from the user's
request, the selected process profile, or the simulator configuration.

## Required Boundary
Design_scope   : on_chip_core_only
Reference_plane:             # on_chip_output_node / schematic_output_node / custom
Process        :
VDD            :
f0             :
R_test_load    :             # Test load or transformed-load equivalent used in schematic simulation
Pout_target    :             # W or dBm at the defined on-chip/output-test reference load
PA_class       :             # A / AB / B / C / E / F / auto / custom

## Active Reliability Limits
f_max_pad      :             # Active only if the pad path is in scope
I_pad_max      :             # Active only if the pad path is in scope
Max_Idc_total  :
Max_output_current_rms :
Max_output_current_pk  :
Max_device_voltage     :
Max_current_density    :

## Active On-Chip Core Performance Targets
Gain_target    :
Pin_available  :
PAE_target     :
Drain_eff_target :
P1dB_target    :
AMPM_max       :
AMAM_error_max :
H2_max_dBc     :
H3_max_dBc     :
Stability_K_min:
Stability_mu_min:

## Passive / Model Scope
Passive_scope  : schematic_available_only
Passive_model_level :
On_chip_passives_allowed :
Inductor_Q_assumed  :
Capacitor_Q_assumed :
Large_inductors_allowed_on_chip :
Off_chip_or_package_match_allowed : advisory

## Simulation Options
Backend         :
Run_Sparams_estimate :
Run_large_signal     :
Run_harmonics        :
Run_power_sweep      :
Run_load_mismatch    :

## Advisory / Residual Items
S11_target      :
S22_target      :
Load_mismatch_VSWR :
Package_model   :
Pad_ESD_model   :
EM_extraction   :
Layout_parasitics:

## Notes
# For on-chip-core-only work, final external return loss, VSWR ruggedness,
# package/bondwire effects, and EM/layout closure are residual unless modeled.
