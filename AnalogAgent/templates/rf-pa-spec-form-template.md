# RF Power Amplifier Spec Form

This is a generic form. Fill values from the active design request, PDK, or
simulator setup. Do not treat blanks or examples elsewhere in the repository as
defaults for this form.

## Required (RF PA sizing will not proceed without these)
Design_scope   :             # on_chip_core_only / full_pa_with_package / unspecified
f0             :             # Center frequency (Hz)
VDD            :             # Supply voltage (V)
Pout_target    :             # Delivered output power (W or dBm)
R_load         :             # External or test load impedance (ohm or complex)
PA_class       :             # A, AB, B, C, E, F, G, H, or auto
Candidate_classes :          # Optional if PA_class=auto
Process        :             # PDK / device family

## Reliability / Implementation Limits
f_max_pad      :             # Highest usable RF frequency through pads, if known
I_pad_max      :             # Pad or package current limit (A), if active
Pdc_max        :             # Max DC input power (W), if active
Iout_rms_max   :             # Output RMS current limit (A), if active
Iout_pk_max    :             # Output peak current limit (A), if active
Max_device_voltage :         # Max allowed device terminal stress (V)
Max_Vds_margin     :         # V; require max transient Vds <= limit - margin
Max_Idc_total      :         # Total DC current limit (A)
Max_current_density:         # A/um or process/layout-specific limit, if known

## Environment
Temperature    :             # C
Corner         :             # Process corner name

## Architecture Intent
Implementation :             # single-ended / differential / auto
Topology       :             # common_source / cascode / stacked / auto / custom
Driver_stages  :             # Number of driver/pre-driver stages
Output_match   :             # L_match / transformer / ideal_load_pull / auto / custom
Input_match    :             # L_match / resistive / transformer / none / auto / custom
Differential_to_SE :         # yes/no, for transformer or balun outputs

## Passive / Reference-Plane Intent
Passive_scope  :             # schematic_available_only / on_chip / package / off_chip / mixed / em_extracted
Passive_model_level :        # ideal / finite_Q_lumped / pdk_model / em_extracted
On_chip_passives_allowed :   # caps_resistors_only / caps_resistors_small_inductors / all_pdk_modeled
Off_chip_or_package_match_allowed : # no / advisory / yes_modeled
Reference_plane:             # schematic_output_node / pad / package_pin / board_50ohm / custom

## RF Performance Targets (leave blank to skip as an active constraint)
Gain_target    :             # Power gain target (dB)
Pin_available  :             # Available input power at nominal output (dBm or W)
PAE_target     :             # Power-added efficiency target (%)
Drain_eff_target :           # Drain efficiency target (%)
P1dB_target    :             # Output P1dB target (dBm or W)
AMPM_max       :             # Max AM/PM at Pout_target (degrees)
AMAM_error_max :             # Max AM/AM gain compression at Pout_target (dB)

## Matching / Bandwidth Targets
Bandwidth      :             # Usable RF bandwidth around f0 (Hz)
Load_Q         :             # Initial matching-network loaded Q target
Match_loss_max :             # Max allowed output matching loss (dB)
S11_max        :             # Input return loss target (dB)
S22_max        :             # Output return loss target (dB)

## Stability Targets
Stability_K_min  :           # Rollett K target, if used
Stability_mu_min :           # Mu target, if used
Stability_fmin   :           # Stability sweep start (Hz)
Stability_fmax   :           # Stability sweep stop (Hz)
Neutralization   :           # none / auto / cross_coupled_cap / custom

## Load Mismatch / Ruggedness
Max_output_current_rms :     # RF load RMS current limit (A)
Max_output_current_pk  :     # RF load peak current limit (A)
Load_mismatch_VSWR     :     # Optional mismatch robustness target

## Harmonics / Spectral Targets
H2_max_dBc      :            # 2nd harmonic limit relative to fundamental (dBc)
H3_max_dBc      :            # 3rd harmonic limit relative to fundamental (dBc)
Spur_max_dBc    :            # Optional spur limit
EVM_max         :            # Optional (%), for modulated simulations
ACLR_max        :            # Optional (dBc)
PAPR            :            # dB

## Simulation Options
Backend         :            # CircuitCollector / SpectreRF / ADS / ngspice / custom / none
Run_Sparams     :            # yes/no
Run_large_signal:            # yes/no
Run_load_pull   :            # yes/no
Run_harmonics   :            # yes/no
Run_modulated   :            # yes/no

## Post-Sizing Options
Extreme_PVT     :            # yes/no
Optimize        :            # yes/no

## Notes
# State which values came from the user, PDK, package model, simulator config,
# or an explicit example. Unspecified values must remain assumptions or
# advisory/residual items until supplied.
