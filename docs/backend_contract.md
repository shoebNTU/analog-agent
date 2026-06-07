# Backend Contract

Each circuit type should have four matching pieces:

```text
AnalogAgent/skills/<skill-name>/
CircuitCollector/CircuitCollector/config/gf180mcuD/<circuit_type>/
CircuitCollector/CircuitCollector/circuits/<circuit_type>/
CircuitCollector/CircuitCollector/spec_lib/<circuit_type>/
```

## Required Config Fields

Every TOML config should include:

```toml
[tech]
name = "gf180mcuD"

[type]
name = "<circuit_type>"

[<circuit_type>]
name = "<template_directory_name>"

[tech_lib]
pdk_path = "PDK/gf180mcuD"
corner = "typical"

[circuit.params_file]
use_params_file = false
generate_params_file = false
API_mode = false

[circuit.params]
# sizing values consumed by circuits/<circuit_type>/<name>/netlist.j2
```

Circuit-specific testbench sections should live under `[testbench.*]`.
Per-call API overrides that are not sizing parameters must be routed in
`CircuitCollector/sim_api.py`; otherwise they may be treated as circuit sizing
parameters.

## Required Templates

Each circuit type needs:

```text
spec_lib/<circuit_type>/main.j2
spec_lib/<circuit_type>/circuit.j2
spec_lib/<circuit_type>/simulation.j2
circuits/<circuit_type>/<name>/netlist.j2
```

The `main.j2` file should include the rendered circuit, tech, and simulation
blocks. The `simulation.j2` file should write scalar measurement files that the
result parser can read.

## Smoke-Test Expectations

A useful smoke test should verify:

- Config and netlist files exist.
- The API accepts the config.
- ngspice runs without fatal errors.
- At least one scalar metric is parsed.
- Missing metrics are reported honestly, not silently treated as passing.

