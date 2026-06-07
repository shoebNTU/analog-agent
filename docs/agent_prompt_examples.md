# Agent Prompt Examples

These prompts assume the agent is opened from the `share_GF180_Analog` folder
after the setup notebook has started a healthy CircuitCollector API.

## RF Power Amplifier

```text
I want to design and review a GF180MCU-D RF power amplifier.

Container: <container_id_or_name>
CircuitCollector API: http://localhost:8001/simulate/

Run all simulations in the container environment. Do not run ngspice or
CircuitCollector from the host Python environment.

Use this nominal starting spec:
- Design scope: on-chip core only
- Process: GF180MCU-D
- VDD: 3.3 V
- f0: 250 MHz
- Load: 50 ohm
- Target Pout: 2 mW
- PA_class: auto
- Max DC power: 33 mW
- Max total DC current: 10 mA
- Max output RMS current: 10 mA
- Max output peak current: 10 mA
- Max device voltage: 3.3 V
- Passive scope: finite-Q schematic passives only; no EM/layout signoff
```

## Analog Amplifier

```text
I want to design and review a GF180MCU-D analog amplifier.

Container: <container_id_or_name>
CircuitCollector API: http://localhost:8001/simulate/

Run all simulations in the container environment. Do not run ngspice or
CircuitCollector from the host Python environment.

Use this nominal starting spec:
- Design scope: schematic-level amplifier
- Process: GF180MCU-D
- Supply: 3.3 V
- Candidate topologies: 5T OTA or two-stage Miller op-amp
- Load capacitance: 2 pF
- Target DC gain: at least 40 dB
- Target unity-gain bandwidth: at least 1 MHz
- Target phase margin: at least 60 deg
- Power: minimize while meeting specs
```

## New Circuit Type Template

```text
I want to design and review a GF180MCU-D <circuit type>.

Container: <container_id_or_name>
CircuitCollector API: http://localhost:8001/simulate/

Run all simulations in the container environment. Do not run ngspice or
CircuitCollector from the host Python environment.

Use this nominal starting spec:
- Design scope: <schematic / on-chip core / full reference plane>
- Process: GF180MCU-D
- Supply: <volts>
- Key target 1: <value>
- Key target 2: <value>
- Key limits: <voltage/current/power/frequency limits>
- Signoff exclusions: <layout, EM, package, pads, etc. if not modeled>
```

