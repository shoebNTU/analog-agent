# GF180 gm/Id Assets

Place processed GF180 MCU-D gm/Id LUT files here.

Recommended layout:

```text
asset_gf180mcuD/
  nfet_03v3/
    tt/
      25C/
        processed/
  pfet_03v3/
    tt/
      25C/
        processed/
```

The exact device names, corners, and temperatures should match the naming
convention used by your GF180 characterization flow.

Do not copy the Sky130 LUTs into this folder. The agent must use technology-
correct characterization data.