# Class-F Harmonic-Tuned RF PA Equations

Use with `general/reference/rfpa-equation-framework.md`.

## Harmonic Termination Targets

Class F shapes voltage/current waveforms by controlling harmonic impedances.
For the usual voltage-square/current-half-wave intuition:

```text
Z_load(f0) = selected fundamental load
Z_load(2*f0) -> short or low impedance for voltage waveform shaping
Z_load(3*f0) -> open or high impedance for voltage waveform shaping
```

Inverse Class F swaps the harmonic open/short intent. The selected variant must
be stated.

## Fundamental Load

Start from the required delivered power and allowed fundamental drain swing:

```text
Rfund = Vfund_pk^2 / (2 * Pout_target)
```

Then load-pull around `Rfund` with finite-Q harmonic terminations.

## Waveform And Stress

Verify:

```text
max(Vds_waveform) <= active stress limit
max(Ids_waveform) <= active current limit
Pout_fundamental >= target
H2/H3 targets pass or are intentionally shaped
```

Harmonic traps can increase circulating current; recheck load mismatch and K/mu
after every harmonic-network change.

