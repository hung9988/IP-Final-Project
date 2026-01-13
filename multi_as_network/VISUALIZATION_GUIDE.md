# Network Visualization Tool

## Quick Usage

### Generate Network Diagram (No GUI Required)

```bash
# Generate diagram with default name
python3 visualize_topology.py

# Generate with custom filename
python3 visualize_topology.py my_network.png
```

This will create:
- **PNG file** (high resolution, 300 DPI)
- **PDF file** (vector format, perfect for documentation)

### Features

✅ **AS-based clustering** - Routers grouped by Autonomous System  
✅ **Color-coded boundaries**:
  - 🔴 Tier 1 (AS 100) - Red/Pink box
  - 🔵 ISP #1 (AS 200) - Blue box  
  - 🟢 ISP #2 (AS 300) - Green box

✅ **Link types**:
  - 🔵 Blue solid = RIP
  - 🟢 Green solid = OSPF
  - 🔴 Red solid = BGP
  - 🟣 Purple dashed = Peering
  - ⚫ Gray = Host connections

✅ **IGP labels** shown in each AS box

### GUI Version (Requires X11 Display)

If you have a display available:

```bash
python3 topology_editor.py
```

Then click the **"Visualize"** button to see the interactive diagram.

### Files Generated

- `network_diagram.png` - High-res image (300 DPI)
- `network_diagram.pdf` - Vector format for printing

### Example Output

The diagram shows your complete 3-AS topology with:
- 9 routers (R1-R9) as white squares
- 4 hosts (PC1-PC4) as teal circles
- All interconnections with proper link types
- AS boundaries with labels and IGP information

Perfect for documentation, presentations, or understanding the network structure!
