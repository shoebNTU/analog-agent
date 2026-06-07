# Adding A New Circuit Type

Use the included `opamp` and `rfpa` backends as examples.

## 1. Add The Agent Skill

Create:

```text
AnalogAgent/skills/<new-skill-name>/
```

The skill should include:

- `SKILL.md` with trigger conditions, rules, and flow order.
- Process notes if GF180-specific assumptions are needed.
- Circuit-specific sizing notes.
- Simulation and design-review expectations.
- At least one example spec.

## 2. Add CircuitCollector Assets

Create:

```text
CircuitCollector/CircuitCollector/config/gf180mcuD/<circuit_type>/
CircuitCollector/CircuitCollector/circuits/<circuit_type>/<topology_name>/
CircuitCollector/CircuitCollector/spec_lib/<circuit_type>/
```

The config's `[type].name` must match `<circuit_type>`.

## 3. Add Result Parsing

If the existing parser does not understand the new circuit's measurement files,
add a parser function in:

```text
CircuitCollector/CircuitCollector/runner/result_parser.py
```

Then dispatch to it from:

```text
CircuitCollector/CircuitCollector/runner/simulation_runner.py
```

## 4. Add API Override Routing

If the API should accept non-sizing knobs such as measurement toggles, route
them in:

```text
CircuitCollector/CircuitCollector/sim_api.py
```

Do not let testbench flags fall into `[circuit.params]`.

## 5. Add Coverage And Smoke Tests

Add or extend a script that can answer:

- Are the expected TOML configs present?
- Are the expected netlist templates present?
- Can a quick simulation run through the API?
- Which metrics are parsed?
- Which metrics are still missing?

## 6. Add Documentation

Add:

- A nominal example spec.
- A compact agent prompt.
- A design-review format with active specs, advisory items, residual risks, and
  known backend limitations.

