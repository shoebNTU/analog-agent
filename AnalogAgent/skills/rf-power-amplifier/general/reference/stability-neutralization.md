# PA Stability and Neutralization

## Stability Checks

Run S-parameter stability checks at low, center, high, and out-of-band
frequencies. Prefer a broad span such as `f0/10` to `10*f0` initially.

Common metrics:

```text
Delta = S11*S22 - S12*S21
K = (1 - |S11|^2 - |S22|^2 + |Delta|^2) / (2*|S12*S21|)
Unconditionally stable if K > 1 and |Delta| < 1.
mu > 1 is also commonly used.
```

## Stability Risks

- High gain and large output swing increase oscillation risk.
- Gate-drain/Miller capacitance creates reverse feedback from output to input.
- Layout, bondwire, package, transformer, and supply parasitics can add
  resonances not visible in schematic-only simulation.
- Driver + output stages may oscillate through interstage matching.

Treat stability as a first-class PA spec, not a cleanup task after Pout/PAE.
Large-signal swings, package/layout parasitics, and matching-network resonance
can invalidate a schematic-only small-signal pass.

## Fixes

Use the least destructive fix that preserves specs:

1. Add or improve cascode isolation.
2. Add differential cross-coupled neutralization caps.
3. Add gate resistors or damping in matching networks.
4. Reduce stage gain or split gain across driver stages.
5. Improve supply decoupling and layout isolation.
6. Re-tune input/interstage/output match after stability changes.

## Neutralization

For differential common-source PAs, cross-coupled neutralization capacitors can
cancel effective gate-drain feedback. Start with:

```text
Cn ~= Cgd_eff
```

Then sweep `Cn` around that value. Check stability, gain, bandwidth, and AM/PM.
Mismatch or parasitic imbalance can leave residual feedback, so do not assume
perfect cancellation.

## Stability Evidence Checklist

Before accepting a topology, report:

- Frequency span and points used for K/mu/Delta or equivalent stability metric.
- Whether S-parameter parsing or port orientation was sanity-checked.
- S12/Miller feedback risk and whether cascode, neutralization, damping, or
  feedback was used.
- Stability before and after any input/output/interstage match changes.
- Whether package, bondwire, pad, supply, and layout parasitics are included or
  residual.
