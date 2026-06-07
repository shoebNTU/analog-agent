# Matching, Load Transformation, and Load-Pull

## Passive Implementation Scope

Before synthesizing or judging a match, classify each passive as one of:

| Scope | Meaning | Simulation treatment |
|---|---|---|
| `on_chip_lumped` | MIM/MOM caps, resistors, small spiral inductors, explicit schematic parasitics | Active if finite-Q values are modeled. |
| `package_or_bondwire` | Bondwire/package inductance, leadframe, package parasitics | Advisory unless package model is present. |
| `off_chip_discrete` | Board-level L/C/matching network, SAW/filter, external balun | Advisory unless included in the simulation netlist. |
| `em_extracted` | Layout-extracted spiral/transformer/pad/route model | Signoff-capable only after extraction exists. |
| `ideal_or_unspecified` | Ideal L/C/transformer/load-pull placeholder | First-pass only; mark Pout/PAE/match as optimistic. |

If the user does not specify passive implementation, default to:

```text
Passive_scope = schematic_available_only
Passive_model_level = finite_Q_lumped when values/Q are known, otherwise ideal_or_unspecified
```

Under this default:

- Simulate only passives that are present in the schematic/config.
- Use finite-Q lumped models for those passives when Q/ESR is available.
- Treat external-reference-plane S11/S22, package matching, bondwire effects,
  off-chip components, and EM/layout closure as advisory or residual.
- Do not fail an `on_chip_core_only` design solely because unmodeled
  off-chip/package passives would be needed for final match closure.
- Do not claim final PA signoff from ideal loads, ideal transformers, or
  load-pull-only terminations.

## Return-Loss Closure Contract

When S11/S22 are poor, first decide whether they are active or advisory.

### Active S11/S22

Treat S11/S22 as active only when the requested reference plane and all matching
elements up to it are represented in the simulation. Then:

1. Extract the simulated input/output impedance at `f0` and across the required
   bandwidth.
2. Synthesize or optimize the input/output match using modeled finite-Q parts.
3. Re-run S-parameters, K/mu, large-signal Pout/gain/PAE, P1dB, harmonics, and
   reliability after every match change.
4. Do not accept SUCCESS until active return-loss targets and all higher-priority
   active specs pass together.

### Advisory S11/S22

If pads, ESD, package, bondwires, off-chip matching, or EM extraction are absent,
do not fail a passing on-chip core solely for final reference-plane return loss. Instead
write a closure contract:

```text
Reference plane modeled now : <schematic node / pad / package / board>
Reference plane needed      : <target plane for S11/S22>
Missing model/scope         : <pad/ESD/package/off-chip/EM/etc.>
Template/API knobs needed   : <input/output match params, finite-Q, package model>
Bounded schematic attempt   : <swept values/results or why deferred>
Activation simulations      : <S-params, stability, large-signal, P1dB, harmonics, mismatch/PVT>
```

The contract is required even when the core report status is SUCCESS.

### Bounded Schematic Improvements

Within `schematic_available_only` scope, it is acceptable to try small bounded
changes that use existing modeled knobs, such as gate damping, output damping,
or modest L/C retuning. Stop the sweep if return-loss improvement degrades
active stability, current/voltage stress, P1dB, harmonics, Pout, gain, or PAE.
Do not describe these changes as package/board reference-plane closure unless that path
is modeled.

## On-Chip vs Off-Chip Choice Heuristics

Use Python to compute candidate L/C values, reactances, Q, current, and area
implications. Then apply these rules:

- Prefer on-chip capacitors and damping resistors when their value, Q, voltage,
  and current stress are reasonable in the PDK.
- Treat large inductors at low RF frequencies as suspicious for on-chip RFIC
  implementation unless the PDK provides an inductor/transformer model and the
  area/Q are acceptable.
- Consider bondwire/package/off-chip inductance for large choke/match values,
  but mark the result advisory until those elements are modeled.
- Prefer off-chip or package matching when the required impedance transform
  needs large inductance, high Q, high current, or final reference-plane return-loss
  closure beyond the on-chip reference plane.
- Keep harmonic traps on-chip only if their finite-Q loss, current, voltage,
  and layout area are modeled; otherwise report them as waveform-shaping seeds.

## First-Pass Load Transform

Given external `R_load` and required device load `R_device`:

```text
transform_ratio = R_load / R_device
```

For a transformer, approximate impedance ratio:

```text
R_primary / R_secondary ~= (N_primary / N_secondary)^2
```

Account for transformer loss. A 1 dB output matching loss reduces delivered
power and PAE materially; include it in budgets when known.

## L-Match Starting Values

Use only for first-pass narrowband matching.

For `R_high > R_low`:

```text
Q = sqrt(R_high / R_low - 1)
X_series = Q * R_low
X_shunt  = R_high / Q
L = X / (2*pi*f0)
C = 1 / (2*pi*f0*X)
```

There are high-pass and low-pass variants. Pick the variant compatible with DC
bias feed, device capacitance absorption, harmonic filtering, and layout.

## Load-Pull Workflow

1. Start from the transformed load derived from `Pout_target`.
2. Sweep complex load impedance around that point at `f0`.
3. Record contours for Pout, PAE, gain, compression, and voltage stress.
4. If harmonic tuning matters, sweep second/third harmonic terminations.
5. Choose a load that satisfies reliability and linearity, not just maximum
   Pout or PAE.
6. Synthesize the matching network for the selected load.
7. Re-simulate with finite-Q passives, package pads, ESD, and extracted layout.

If no load-pull or source-pull is available, mark the load choice as
first-pass analytical or schematic-optimized. Do not describe it as an optimum.

## Harmonic Trap Caution

H2/H3 shunt traps can improve nominal harmonic numbers while making load
mismatch, stability, and current stress worse. Use them only after the
fundamental match is stable and current-safe.

When traps are used:

- Include finite-Q loss and series resistance.
- Sweep load mismatch with traps enabled.
- Compare K/mu and output current before/after each trap.
- If negative-reactance loads create excessive current, lower Q, retune, or
  remove the trap before increasing device width/current.

## Red Flags

- Required `R_device` is below a few ohms: transformer/passive loss and current
  density may dominate.
- Matching Q is too high: bandwidth, loss, and tolerance sensitivity will fail.
- Output capacitance is comparable to match capacitance: absorb it explicitly.
- Load-pull optimum requires voltage/current beyond device limits.
- Required inductors are tens of nH or larger at hundreds of MHz: likely
  package/off-chip candidates unless a PDK passive model proves otherwise.
- The spec asks for final S11/S22 but only an on-chip core schematic is modeled:
  classify return loss as advisory until the missing passive/reference-plane
  model is included.
- Poor advisory S11/S22 without a closure contract: incomplete review.
- A nominal match passes Pout/PAE but fails VSWR=2 current limits: redesign the
  match/load-pull target before treating the nominal result as acceptable.
