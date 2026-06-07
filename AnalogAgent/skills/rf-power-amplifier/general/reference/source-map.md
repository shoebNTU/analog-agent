# RF PA Source Map

Use this file to keep the RF PA skill tied to recognized RFIC references while
keeping the procedural flow simulator- and process-neutral. This is a source
map, not a substitute for the detailed equations, measurements, PDK rules, or
simulator documentation needed for a final design.

## Primary Open Reference

- Harald Pretl, "Radio-Frequency Integrated Circuits", JKU/IIC open course
  notes, Section 8 "Power Amplifiers".
- The course explicitly frames PAs around tradeoffs between efficiency,
  linearity, bandwidth, and cost.
- Section 8.1 covers PA efficiency.
- Section 8.2 covers PA nonlinearity and load-pull style large-signal
  characterization.
- Section 8.3 covers amplifier classes and their conduction-angle,
  efficiency, linearity, and complexity tradeoffs.
- Section 8.4 covers PA stability and neutralization, including Miller feedback,
  cascode isolation, neutralization capacitors, and differential
  cross-coupled neutralization.
- Section 8.5 lists advanced techniques such as predistortion and supply/
  architecture-level efficiency improvements.

URL:
`https://iic-jku.github.io/radio-frequency-integrated-circuits/rfic.html`

## Foundational Textbook Anchors

Use these as conceptual anchors when the user asks for a deeper derivation or
when the open notes are insufficient:

- Behzad Razavi, RF Microelectronics.
- Hooman Darabi, Radio Frequency Integrated Circuits and Systems.
- David M. Pozar, Microwave Engineering, especially for matching, S-parameters,
  and microwave network concepts.

## Skill Coverage Mapping

| Source topic | Skill file(s) that must cover it | Required design evidence |
|---|---|---|
| PA efficiency | `pa-metrics.md`, `design-review.md` | Pdc, Pout, drain efficiency, PAE, passive/match loss budget |
| PA nonlinearity | `pa-metrics.md`, `simulation-verification.md` | P1dB or compression sweep, AM/AM, AM/PM, modulation/PAPR targets |
| Amplifier classes | `pa-classes.md`, `class-auto-selection.md`, circuit-specific flows | Conduction angle/switching mode, selected class rationale, rejected alternatives |
| Matching and load-pull | `matching-and-load-pull.md`, `student-preflight.md` | Device load, reference plane, finite-Q network, load-pull/source-pull status |
| Stability and neutralization | `stability-neutralization.md`, `root-cause-diagnosis.md` | K/mu or equivalent sweep, S12/Miller risk, cascode/neutralization/damping decision |
| Advanced techniques | `pa-classes.md`, `source-map.md`, circuit-specific flows | DPD/envelope tracking/harmonic tuning/Doherty/outphasing marked used or out of scope |
| Implementation closure | `spec-understanding.md`, `design-review.md` | Process limits, backend status, layout/EM/package/reference-plane closure state |

## Completeness Rule

If a design review omits one of the source topics above, do not describe the RF
PA skill result as comprehensive. Mark the missing topic as:

```text
active: covered with calculation/simulation evidence
advisory: relevant but blocked by missing model/reference plane
out_of_scope: explicitly not required by this task
missing: should have been covered but was not
```

Only `active`, `advisory`, or `out_of_scope` are acceptable final review states.
