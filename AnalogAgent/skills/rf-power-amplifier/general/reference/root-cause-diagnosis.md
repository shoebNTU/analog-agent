# RF PA Root-Cause Diagnosis

Follow this order. Reliability and stability failures outrank performance.

## Nominal Pass But Expanded Checks Fail

If nominal Pout/gain/PAE look acceptable but S-parameters, P1dB/AM-AM/AM-PM, or
load mismatch fail, treat the design as fragile. Do not optimize for more Pout
until these are addressed in order:

1. Fix parser/testbench correctness if raw simulator data and API values differ.
2. Stabilize the active device and matching network.
3. Redesign input/output match using actual device capacitances and the correct
   reference plane.
4. Run load-pull and select a load that satisfies current/voltage limits.
5. Retune compression and AM/AM/AM/PM at the nominal drive point.

If `PA_class = auto`, add a topology feedback tag after diagnosis:

```text
topology_limited              current topology cannot clear an active failure
network_incomplete            topology is plausible but required match/trap/load network is missing
drive_or_headroom_limited     driver/interstage/output swing must be repartitioned
advisory_limited              failure depends on unmodeled package/off-chip/layout scope
```

Return to class auto-selection when the tag is `topology_limited`. Stay in the
same topology when the tag is `network_incomplete` or `drive_or_headroom_limited`
and the missing network/drive change is implementable in the current template.

## Device Stress Too High

```
max |Vds(t)| or |Vgs(t)| > limit
  -> reduce output swing or transformed load impedance
  -> add/use cascode or stacked devices
  -> use thick-oxide devices where allowed
  -> reduce VDD or Pout target
  -> re-check waveform and harmonic terminations
```

## Unstable or Marginal Stability

```
K <= 1, mu <= 1, oscillation, or negative resistance
  -> reduce reverse isolation: cascode or neutralization
  -> add damping/gate resistance
  -> add output-network damping or lower loaded Q
  -> remove/retune high-Q harmonic traps that introduce resonances
  -> reduce stage gain or add buffering
  -> rework matching network Q and resonances
  -> include package/layout/supply parasitics
```

## Poor Input/Output Return Loss

```
S11/S22 worse than target
  -> first verify parser/raw-file column mapping
  -> define the reference plane: on-chip node, pad, package, board load, or custom
  -> classify the target as active or advisory from modeled passive scope
  -> if active, extract Zin/Zout and synthesize/optimize the modeled match
  -> absorb Cgs/Cgd/Cds and pad capacitance into the match
  -> redesign the input/output match around the simulated device impedance
  -> add damping if return-loss improvement worsens K/mu or load mismatch
  -> if advisory, write the match-closure contract instead of failing the core
  -> keep final reference-plane match advisory when package/off-chip match is unmodeled
```

Diagnosis tags:

```text
network_incomplete
  Use when S11/S22 are active and the current modeled match cannot meet target.
  Stay in the current topology if active reliability, stability, linearity,
  harmonics, Pout, gain, and PAE already pass; update/optimize the match before
  trying a new PA class.

advisory_limited
  Use when S11/S22 are poor only because package/off-chip/pad/EM scope is
  missing. Do not switch topology solely for this. Produce the closure contract
  and list the model/template additions required to make S11/S22 active.
```

## Load Mismatch Current/Voltage Failure

```
VSWR/load-pull stress exceeds current or voltage limit
  -> do not accept the nominal reference-plane result
  -> reduce output-network Q and harmonic-trap sharpness
  -> choose load-pull point by current/voltage contours, not only Pout/PAE
  -> add protection/damping or reduce target Pout
  -> move large/high-Q matching elements to modeled package/off-chip network
  -> re-run mismatch sweep after every match/harmonic-network change
```

## Pout Too Low

```
Pout < target
  -> check device load from matching network; run load-pull
  -> increase voltage swing if reliability margin exists
  -> increase device width/current if gain or current limit is binding
  -> reduce matching/passive loss
  -> add/resize driver if input drive is insufficient
  -> if VDD-limited, lower device load impedance via transformer/match
```

## PAE or Drain Efficiency Too Low

```
efficiency < target
  -> reduce DC bias for Class AB/B/C if linearity allows
  -> reduce matching loss and transformer loss
  -> tune harmonic terminations for waveform shaping
  -> avoid over-driving driver stages
  -> consider envelope tracking/Class G/H for backed-off operation
```

## Gain Too Low

```
gain < target
  -> improve input/interstage/output matching
  -> increase gm/device width or bias in driver/final stage
  -> reduce load seen by prior stage from large final gate capacitance
  -> add driver/pre-driver, then re-check stability
```

## Linearity / AM-AM / AM-PM / ACLR / EVM Failure

```
linearity fails
  -> if nominal Pin is beyond P1dB, back off drive or resize/rebias before
     claiming nominal Pout
  -> back off output power or increase device/headroom
  -> bias closer to Class A/AB
  -> linearize match or reduce Q if memory effects dominate
  -> use predistortion/feedback/envelope tracking if architecture allows
  -> inspect AM/AM and AM/PM separately; do not diagnose from P1dB alone
```

## Bandwidth Too Narrow

```
bandwidth < target
  -> lower matching Q
  -> reduce/neutralize Cgd feedback
  -> absorb device capacitance into matching network
  -> reduce transformer/passive Q sensitivity
  -> use staggered or broadband matching
```

## Thermal Risk

```
power dissipation too high
  -> improve efficiency before increasing current
  -> reduce duty cycle or Pout
  -> estimate junction temperature with layout/package thermal model
  -> flag that signoff requires thermal simulation
```
