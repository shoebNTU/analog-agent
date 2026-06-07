# RF PA Topology Understanding

## Purpose

Given an RF PA netlist or selected PA class, identify the topology, select the
matching circuit-specific flow, and determine whether the selected simulator
backend can support credible simulation evidence.

## Supported Topology Seeds

| Pattern | Classification | Skill directory | Backend implementation | Simulation status |
|---|---|---|---|---|
| Single-ended common-source, biased for 360 deg conduction | Class-A single-ended | `circuit-specific/class-a-single-ended/` | backend-specific | check adapter/config |
| Single-ended common-source, partial conduction | Class-AB single-ended | `circuit-specific/class-ab-single-ended/` | backend-specific | check adapter/config |
| Driver stage feeding larger final common-source stage | Two-stage single-ended | `circuit-specific/two-stage-single-ended/` | backend-specific | check adapter/config |
| Differential/push-pull output devices | Class-B differential | `circuit-specific/class-b-differential/` | backend-specific | check adapter/config |
| Differential cascode with transformer/balun matching | Differential cascode transformer | `circuit-specific/differential-cascode-transformer/` | backend-specific | check adapter/config |
| Below-threshold/short-conduction tuned load | Class-C tuned | `circuit-specific/class-c-tuned/` | backend-specific | check adapter/config |
| Switch device + RF choke + shunt capacitance + series load network | Class-E switching | `circuit-specific/class-e-switching/` | backend-specific | check adapter/config |
| Fundamental load plus 2f0/3f0 harmonic terminations | Class-F harmonic tuned | `circuit-specific/class-f-harmonic-tuned/` | backend-specific | check adapter/config |

If the selected backend implementation is scaffold-only, it may be used for
class ranking and first-pass sizing notes, but not for final simulation
evidence.

## Accepted Inputs

The skill accepts any of these inputs:

| Input | How to handle |
|---|---|
| Filled RF PA spec with `PA_class` | Select class-specific flow from the table above. |
| `PA_class = auto` with candidate classes | Run `class-auto-selection.md`, then select the best available flow. |
| Raw PA netlist | Parse devices, ports, passives, biasing, and matching; map to the closest supported seed. |
| Textbook archetype or figure description | Map the described circuit to the closest supported seed; do not assume a runnable backend implementation exists. |
| Existing simulator/backend config | Read backend-specific topology name, simulation enablement, and validation status before simulation. |

## Procedure

### Step 1 - Parse Netlist or Existing Config

Identify:

1. **Signal path**: input matching, driver stages, final stage, output matching.
2. **Topology**: common-source, cascode, stacked, transformer-coupled,
   differential, push-pull, switching/tuned.
3. **Class clues**:
   - Class A/AB/B/C from gate bias and conduction angle.
   - Class E/F from switch-like device, choke/feed, shunt capacitance, and
     harmonic-tuned load network.
   - Class G/H/envelope tracking from multiple/adaptive supplies.
4. **Ports and loads**: RF input, RF output, VDD, VSS, bias ports, specified
   load/reference plane, baluns/transformers.
5. **Reliability structures**: cascodes, thick-oxide devices, stacked supplies,
   clamp/ESD/loading that may affect RF behavior.
6. **Stability aids**: neutralization caps, feedback, damping resistors, gate
   resistors, isolation/cascode devices.

### Step 2 - Assign Functional Roles

Use these role names consistently:

| Role | Meaning |
|---|---|
| `INPUT_MATCH` | Input AC coupling, L/C match, gate damping, source resistance |
| `DRIVER` | Optional pre-driver or intermediate RF stage |
| `OUTPUT_DEVICE` | Final power transistor or switch device |
| `CASCODE` | Voltage-stress sharing or reverse-isolation device |
| `BIAS_NETWORK` | Gate/drain bias source, current mirror, RF choke, bias feed |
| `OUTPUT_MATCH` | Fundamental load transform or tuned output network |
| `HARMONIC_NETWORK` | H2/H3 traps or Class-F terminations |
| `BALUN_COMBINER` | Differential splitter, combiner, transformer, balun |
| `STABILITY_AID` | Gate stopper, shunt damping, feedback, neutralization |

### Step 3 - Select Circuit-Specific Flow

Map the identified class/topology to exactly one `circuit-specific/` directory.
If the class is ambiguous, choose the conservative lower-risk flow and state the
assumption. If no supported topology matches, stop and report the supported
topologies instead of inventing a sizing procedure.

### Step 4 - Backend Readiness Gate

Before running simulation, check the selected backend adapter/config. For
CircuitCollector, read `backends/circuitcollector.md` and inspect:

```toml
[rfpa]
simulation_enabled = true/false
validation_status = "..."
```

- If `simulation_enabled = true`, the config may be simulated.
- If `simulation_enabled = false`, do not simulate it; use the flow only for
  first-pass sizing and candidate ranking.
- If the config is missing, report that the class is not registered in the
  selected backend.

## Mandatory Output

```
RF PA TOPOLOGY IDENTIFICATION
=============================
Topology        : <name>
PA class        : <A/AB/B/C/E/F/G/H/unknown>
Implementation  : single-ended / differential
Stages          : <driver count + output stage>
Matching        : input=<type>, interstage=<type>, output=<type>
Load transform  : <external load> -> <device load or unknown>
Stability aids  : <cascode / neutralization / feedback / damping / none>
Reliability     : <stacking / thick oxide / unknown>
Skill flow      : circuit-specific/<selected-topology>/*-design-flow.md
Backend         : <backend or none>
Backend mapping : <template/config/netlist/custom/none>
Backend status  : runnable_seed / scaffold_only / missing / custom
Simulation need : HB / transient RF / S-param / load-pull / EM extraction
```

If topology or class is ambiguous, proceed with a conservative assumption and
state it. Do not stop unless pin/function ambiguity prevents simulation.

## Next Stage

Proceed to class auto-selection if needed; otherwise proceed to the selected
`circuit-specific/<topology>/*-design-flow.md`.
