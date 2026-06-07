# GF180 Opamp Configs

This directory contains ready-to-use GF180MCU-D op-amp TOML configs for the
bundled 5T OTA and two-stage Miller op-amp examples.

Runnable configs:

- `5tota_single.toml`
- `5tota_single_gf180.toml`
- `tsm_single.toml`
- `tsm_single_gf180.toml`

The `_gf180` configs are aliases used by the setup notebook and agent prompts.
Their matching netlist templates live under:

- `CircuitCollector/CircuitCollector/circuits/opamp/5tota_single_gf180/`
- `CircuitCollector/CircuitCollector/circuits/opamp/tsm_single_gf180/`

The GF180 PDK is not bundled. The setup notebook creates
`CircuitCollector/CircuitCollector/PDK/gf180mcuD` as a symlink to the PDK path
inside the connected IIC-OSIC-TOOLS container.
