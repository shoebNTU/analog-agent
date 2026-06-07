# PA Class Selection

Use this file for class tradeoff background. If `PA_class = auto` or
`Candidate_classes` is present, also read `class-auto-selection.md`.

| Class | Conduction | Efficiency | Linearity | Use When |
|---|---:|---|---|---|
| A | 360 deg | low | high | maximum linearity, low Pout |
| B | 180 deg | medium | medium | sinusoidal/push-pull, moderate linearity |
| AB | 180-360 deg | medium | medium-high | linear RF PA default |
| C | <180 deg | high | low | constant-envelope or tuned narrowband |
| D/E/F | switching/tuned | very high | low to medium | efficiency-first, harmonic tuning available |
| G/H | multi/adaptive supply | very high | medium | envelope tracking / supply modulation |

## Selection Rules

1. If modulation has high PAPR or linearity/EVM/ACLR is active, prefer Class AB
   unless the user explicitly requests switching/envelope tracking.
2. If the signal is constant-envelope and efficiency dominates, consider Class C
   or switching classes.
3. If `Pout_target` is high relative to `VDD` and the specified load,
   prioritize load transformation and voltage stress before bias class details.
4. If mobile/battery efficiency is important and linearity remains active,
   mention Class AB plus envelope tracking (Class G/H style) as an advanced path.
5. If the requested class cannot meet linearity or reliability, report the
   conflict before sizing.

## Fixed-Class Rule

If the spec fixes `PA_class`, obey it unless it violates hard safety/reliability
limits. You may recommend alternatives, but do not silently switch class.

## Auto-Class Rule

If `PA_class = auto`, use `class-auto-selection.md` to rank candidates. Only
claim automatic optimization for classes that have topology templates/netlists
and comparable simulations.

## Advanced Techniques Gate

Before finalizing class selection, explicitly decide whether these are in scope:

| Technique | Use when | Required evidence |
|---|---|---|
| Harmonic tuning / Class F or inverse-F | Efficiency-first narrowband PA | H2/H3 termination model, waveform stress, finite-Q loss |
| Envelope tracking / Class G/H | Modulated signal with high efficiency pressure | Supply modulator model or explicit system-level assumption |
| Digital predistortion | Linearity target is tight and digital correction is available | AM/AM and AM/PM fit, DPD residual or advisory note |
| Doherty / load modulation | High average efficiency over output backoff is required | Main/peaking paths, combiner/load modulation model |
| Outphasing / polar | Efficiency-first architecture with phase/amplitude path support | Combiner loss, bandwidth, and modulation-path evidence |

If none apply, write `Advanced techniques: out_of_scope` in the design review.
