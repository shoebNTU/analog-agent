# PA Class Auto Selection

Use this file when `PA_class = auto`, `Candidate_classes` is present, or the
requested class conflicts with the active specs.

## Candidate Policy

Default candidate set for CMOS on-chip schematic exploration:

```
A, AB, B, C
```

Only include `E` or `F` when all are true:

- constant-envelope or efficiency-first operation is explicitly requested
- harmonic terminations are in scope
- finite-Q passive loss and device voltage stress are checked
- the user accepts switching/tuned waveform risk

Only include `G` or `H` when envelope tracking or adaptive/multi-level supply is
explicitly in scope. Otherwise report it as an advanced architecture option, not
a normal candidate.

## Scorecard

Evaluate each candidate with Python and simulation evidence. Use this scoring
order:

1. Reject candidates that violate hard reliability limits:
   `Vdevice`, `Idc_total`, `Iout_rms`, `Iout_pk`, pad frequency/current limits.
2. Reject candidates that cannot plausibly meet active linearity/modulation
   requirements.
3. Reject candidates whose required load/matching cannot be represented by the
   modeled on-chip/package scope.
4. Among survivors, rank by:
   - meeting Pout/gain/PAE/drain-efficiency targets
   - compression and AM/AM/AM/PM margin
   - harmonic margin
   - stability/matching risk
   - implementation complexity

## Heuristics

| Spec condition | Prefer | Avoid or mark risky |
|---|---|---|
| High linearity, high PAPR, EVM/ACLR active | A, AB | C, E, F unless linearization is in scope |
| Modest linearity, efficiency desired | AB, B | A if current budget is tight |
| Constant-envelope narrowband, efficiency dominant | C, E/F with tuned load | A |
| On-chip-only, limited passive/Q model | A, AB, B, C | E/F unless harmonic network is explicitly modeled |
| Tight voltage stress and pad/current limits | A/AB with conservative swing, possibly B | switching classes without stress proof |
| Need final external-reference-plane S11/S22 but no package/off-chip match | no class can close alone | treating class change as match closure |

## Auto-Selection Procedure

1. Parse `PA_class`.
2. If fixed, obey it, but still run this conflict check:
   - If a different class is likely better, report as an alternative, not the
     chosen implementation.
3. If `PA_class = auto`:
   - Build candidate list from `Candidate_classes`; otherwise use default.
   - For each candidate, derive first-pass `Idc`, device load, expected
     efficiency, swing/current stress, and required matching.
   - Mark each candidate as `reject`, `simulate`, or `defer`.
   - Simulate only candidates with a local topology/netlist template.
   - Pick the lowest-risk passing candidate. If none pass, return ranked
     failure causes and the least-bad next candidate.

## Feedback-Driven Topology Switching

After each simulated candidate, classify the failure mode and decide whether
local tuning is still justified or whether the next topology must be tried.
Use simulation evidence, not intuition.

| Failure after bounded local search | Mark current topology | Next runnable topology preference |
|---|---|---|
| Active reliability failure | reject | lower swing/load, cascode/stacked device, or lower Pout |
| Active K/mu stability failure | topology_limited | cascode, differential, neutralized, or two-stage isolated topology |
| Pout/gain/PAE pass but P1dB/AM-AM fails | topology_or_drive_limited | driver/final split, reduced interstage drive, more headroom |
| Pout/gain/PAE/current/stability pass but H2/H3 fail | network_incomplete | same topology with harmonic network, or harmonic-tuned template |
| Final S11/S22 fail at a modeled reference plane | network_incomplete | keep otherwise passing topology and optimize modeled input/output match |
| Final S11/S22 fail only under schematic_available_only scope | advisory_limited | do not switch class solely for unmodeled package/off-chip match; write closure contract |
| Load mismatch fails and mismatch is active | network_or_protection_limited | load-pull-selected match, transformer/package/off-chip model, protection/damping |

When no candidate passes all active specs, select the next development topology
by the highest-priority active failure it resolves. For example, if a
single-stage Class-AB seed passes nominal Pout/gain/linearity but fails K/mu,
and a two-stage seed passes K/mu but fails harmonics, choose the two-stage seed
as the next development path because stability outranks harmonic cleanup.
Report the selected topology as "least-bad next path", not "SUCCESS".

S11/S22 are lower priority than active reliability, stability, linearity,
harmonics, and nominal power metrics. A class change is not a valid fix for poor
final reference-plane match when the missing object is a package/off-chip/pad/EM model.
In that case, keep the passing core topology and require the match-closure
contract from `matching-and-load-pull.md`.

## Required Output

```
PA CLASS AUTO-SELECTION
=======================
Candidate | Decision | Main reason | Required topology/template | Feedback status | Risks
A         | reject/simulate/defer | ... | ... | ... | ...
AB        | reject/simulate/defer | ... | ... | ... | ...
B         | reject/simulate/defer | ... | ... | ... | ...
C         | reject/simulate/defer | ... | ... | ... | ...

Selected class: <class or none>
Why: <short justification>
Alternatives: <ranked list>
Next topology action: <continue selected / try next runnable / update template>
```

## Important Limits

Do not claim automatic class optimization unless candidate netlists/templates
exist and all active metrics have been simulated under comparable assumptions.
If only one topology is implemented, auto-selection may recommend a class but
must not pretend it has completed multi-class verification.
