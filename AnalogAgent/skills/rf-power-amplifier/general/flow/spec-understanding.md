# RF PA Spec Understanding

## Required Fields

Stop if any of these are missing:

```
Design_scope : on_chip_core_only / full_pa_with_package / unspecified
f0           : center frequency (Hz)
VDD          : supply voltage (V)
Pout_target  : delivered output power (W or dBm)
R_load       : external/test/reference-plane load
PA_class     : target class or "auto"
Process      : PDK / device family
```

## Recommended Fields And Assumptions

Apply assumptions only after printing them. Do not treat these as design
targets, and let a user spec, process profile, or simulator config override
them.

| Field | Fallback assumption | Notes |
|---|---:|---|
| Temperature | ambient / simulator nominal | Use simulation temperature as numeric and LUT temp string if LUTs exist |
| Corner | process nominal | Use PDK corner names |
| Pin_available | blank | Needed for gain and PAE target |
| Reference_plane | schematic_output_node | Use pad/package/board_50ohm only when modeled |
| S11_target / S22_target | blank | Active only when the reference plane and matching path are modeled |
| Candidate_classes | A, AB, B, C when PA_class=auto | Include E/F/G/H only when explicitly in scope |
| Gain_target | blank | Power gain, dB |
| PAE_target | blank | Percent |
| Drain_eff_target | blank | Percent |
| Compression | P1dB target blank | Use large-signal sweep |
| Linearity | blank | EVM/ACLR/IM3/AM-AM/AM-PM target |
| PAPR | 0 dB | Constant-envelope if unspecified |
| Load_Q | 2 to 5 | Start low for bandwidth and loss |
| Differential | infer from netlist | yes/no |
| Backend | blank | Simulator/API backend; no local paths are assumed if blank |
| Max_device_voltage | PDK-dependent | Must be checked against OP/transient |
| Max_current_density | PDK/layout-dependent | Report as assumption if unavailable |
| Extreme_PVT | no | If yes, re-run final sizing at requested slow/fast corners |
| Load_mismatch_check | scope-dependent | Active only when mismatch network/protection/load model is in scope |
| Finite_Q_passives | yes for RFIC | Use finite-Q schematic passives when values are modeled |
| Passive_scope | schematic_available_only | If unspecified, limit active checks to passives present in schematic/config |
| On_chip_passives_allowed | caps/resistors/small_inductors | Large inductors require PDK model or become advisory/off-chip candidates |
| Off_chip_or_package_match_allowed | advisory | May be recommended, but not claimed as simulated unless modeled |

## Scope Classification

Before marking any RF PA spec pass/fail, classify the requirement:

| Requirement | On-chip-core active? | Full PA/package active? |
|---|---|---|
| Voltage/current stress | yes | yes |
| Nominal Pout/gain/PAE/drain efficiency | yes | yes |
| Harmonics from transient waveform | yes | yes |
| P1dB, AM/AM, AM/PM | active if specified | yes |
| Core stability estimate | yes | yes |
| Final reference-plane S11/S22 | active only if the input/output match through the requested reference plane is modeled; otherwise advisory | yes |
| 2:1 VSWR/load mismatch ruggedness | advisory unless protection/mismatch network is in scope | yes |
| Large inductors, off-chip matching, bondwire/package effects | residual/system-level | yes |
| EM/layout extraction | residual until layout exists | yes |

If `Design_scope = on_chip_core_only`, use
on-chip-core semantics: do not fail the on-chip core solely because final
external S11/S22 or VSWR ruggedness is not achieved without modeled
package/off-chip matching. A local on-chip-core form may be used as a
convenience checklist, but it is not a source of default numeric targets.

## Passive Scope Fallback

If the user does not specify whether passives are on-chip, package, or
off-chip, assume:

```text
Passive_scope = schematic_available_only
Passive_model_level = finite_Q_lumped for schematic passives with known Q,
                      ideal_or_unspecified otherwise
Off_chip_or_package_match_allowed = advisory
```

This means the skill should suggest plausible on-chip/package/off-chip passive
partitioning, but active simulation claims are limited to elements actually
present in the schematic/config. Final external/reference-plane S11/S22,
off-chip matching, package/bondwire effects, and EM/layout closure remain
advisory or residual until those models are included.

## S11/S22 Activation Rule

Classify return loss before topology selection:

```text
S11/S22 active when:
  Reference_plane is pad, package pin, or board_50ohm AND
  the input/output matching, pad/ESD, package/off-chip elements up to that
  plane are present in the simulation netlist/config.

S11/S22 advisory when:
  Reference_plane = schematic_output_node, Passive_scope =
  schematic_available_only, or the package/off-chip/pad/EM path is missing.
```

If S11/S22 are advisory but poor, the design can still pass active core specs,
but the flow must emit a match-closure contract listing:

- missing reference-plane model and passive scope;
- backend/template/API knobs needed for input/output match optimization;
- bounded schematic-only damping/match changes that were attempted or deferred;
- exact simulations required to convert S11/S22 from advisory to active.

If required inductors or transformers are very large for the frequency/process,
report them as likely package/off-chip candidates and keep the on-chip-core
simulation bounded to the modeled load/reference plane.

## Post-Sizing Options

Parse these options and carry them through the flow:

- `Extreme_PVT`: if `yes`, run final sizing at the requested slow/hot and
  fast/cold corners. If no corners are specified, use the selected process
  profile's standard slow/hot and fast/cold conditions, or ask for them before
  claiming PVT coverage.
- `Load_mismatch_check`: if `yes` and load mismatch is in modeled scope, run
  the configured gamma/VSWR sweep. If only the on-chip core is modeled, report
  it as advisory unless the mismatch network/protection is included.
- `Finite_Q_passives`: if `yes` or blank, include finite-Q loss for schematic
  inductors, capacitors, transformers, and traps where values are known. If
  ideal passives are used, mark PAE/efficiency as optimistic.

## Mandatory Output

```
VALIDATED RF PA SPECIFICATIONS
==============================
Required:
  Design_scope = <scope>
  f0           = <Hz>
  VDD          = <V>
  Pout_target  = <W> (<dBm>)
  R_load       = <ohm>
  PA_class     = <class/auto>
  Candidates   = <if PA_class=auto>
  Process      = <PDK/devices>
  Backend      = <simulator/API or none>

Active Targets:
  Gain         : <constraint or inactive>
  PAE          : <constraint or inactive>
  Drain eff.   : <constraint or inactive>
  Linearity    : <constraint or inactive>
  Stability    : unconditional / K>1 / mu>1 / custom
  Reliability  : <voltage/current constraints>

Advisory / Residual:
  S11/S22       : <active/advisory and why>
  Load mismatch : <active/advisory and why>
  Passives      : <on-chip/package/off-chip/model scope>
  EM/layout     : <active/advisory/residual and why>
  Match closure : <required model/backend/simulation contract if advisory>

Environment:
  Corner       = <corner>
  Temperature  = <C>

Post-Sizing:
  Extreme PVT  = enabled / disabled
  Load mismatch= active / advisory / disabled
  Finite-Q     = modeled / idealized / unavailable
  Passive scope= schematic_available_only / on_chip / package / off_chip / mixed
```

## Next Stage

Proceed to `general/flow/student-preflight.md` if it has not already been
completed. Otherwise proceed to `general/flow/topology-understanding.md`.
