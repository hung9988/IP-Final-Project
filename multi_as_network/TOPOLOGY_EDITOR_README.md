# Network Topology Editor

A native Python GUI tool for visualizing and editing your Mininet network topology.

## Features

✨ **Visual Topology Browser**
- Tree view of all network components (routers, hosts, links)
- Organized by Autonomous Systems
- View IP addresses and link types

📝 **Configuration Editor**
- Edit FRR configuration files (frr.conf, daemons, vtysh.conf)
- Syntax validation
- Backup on save

📊 **Network Visualization**
- Interactive graph visualization using NetworkX
- Color-coded links by protocol type (RIP, OSPF, BGP)
- Export diagrams as PNG/PDF

📤 **Export Capabilities**
- Export topology to JSON
- Save network diagrams

## Installation

### Dependencies

The tool requires Python 3 with Tkinter (usually included) and optionally:
- `matplotlib` - for network visualization
- `networkx` - for graph layout

Install dependencies:
```bash
pip3 install matplotlib networkx --user
```

Or use the launcher script which auto-installs dependencies:
```bash
./launch_editor.sh
```

## Usage

### Quick Start

1. **Launch the editor:**
   ```bash
   cd /home/hung1fps/final_ip_project/multi_as_network
   python3 topology_editor.py
   ```
   
   Or use the launcher:
   ```bash
   ./launch_editor.sh
   ```

2. **Browse the topology:**
   - The left panel shows a tree view of your network
   - Click on any item to see details in the right panel

3. **Edit configurations:**
   - Go to the "Configuration" tab
   - Select a router from the dropdown
   - Choose the config file (frr.conf, daemons, vtysh.conf)
   - Edit and save

4. **Visualize the network:**
   - Click "Visualize" button in the toolbar
   - A new window will show an interactive graph
   - Save the diagram if needed

### Tabs Overview

#### 📋 Details Tab
Shows detailed information about selected items:
- Router configuration file paths
- Connected links and IP addresses
- Host gateway information

#### ⚙️ Configuration Tab
Edit router configurations:
- **Router selector**: Choose which router to configure
- **Config type**: Select frr.conf, daemons, or vtysh.conf
- **Editor**: Full-featured text editor with syntax highlighting
- **Actions**:
  - **Save**: Save changes (creates backup)
  - **Reload**: Discard changes and reload from file
  - **Validate**: Check for common configuration issues

#### 🗺️ Network Diagram Tab
ASCII art representation of the network topology with:
- All routers and their connections
- IP addressing scheme
- Routing protocols per AS

### Toolbar Functions

- **Refresh**: Reload topology data
- **Visualize**: Open graphical network visualization
- **Export**: Export topology data to JSON

## Network Structure

### Autonomous Systems

| AS | Name | Routers | IGP Protocol |
|----|------|---------|--------------|
| 100 | Tier 1 | R4, R5, R6 | OSPF |
| 200 | ISP #1 | R1, R2, R3 | RIP |
| 300 | ISP #2 | R7, R8, R9 | OSPF |

### BGP Connections

- R2 (AS 200) ↔ R4 (AS 100)
- R6 (AS 100) ↔ R7 (AS 300)
- R2 (AS 200) ↔ R7 (AS 300) - Peering

### Hosts

- **PC1**: Connected to R1 (192.168.1.2/24)
- **PC2**: Connected to R3 (192.168.2.2/24)
- **PC3**: Connected to R8 (192.168.3.2/24)
- **PC4**: Connected to R9 (192.168.4.2/24)

## Tips

💡 **Configuration Editing**
- Always validate before saving
- Backups are created automatically (.bak extension)
- Changes require FRR restart to take effect

💡 **Visualization**
- Different colors represent different link types
- Routers are shown as squares, hosts as circles
- You can save the visualization for documentation

💡 **Workflow**
1. Browse topology to understand structure
2. Edit configurations as needed
3. Save and validate
4. Run `./setup_frr.sh` to apply changes
5. Restart network with `sudo python3 run.py`

## Troubleshooting

**Issue**: "matplotlib not found"
- **Solution**: Run `pip3 install matplotlib networkx --user`

**Issue**: "Permission denied" when saving configs
- **Solution**: Make sure you have write permissions in the directory

**Issue**: Visualization window doesn't open
- **Solution**: Ensure you have X11 forwarding enabled if using SSH

## File Structure

```
multi_as_network/
├── topology_editor.py      # Main GUI application
├── launch_editor.sh         # Launcher script with dependency check
├── topology.py              # Mininet topology definition
├── run.py                   # Network runner script
├── setup_frr.sh            # FRR setup script
└── r[1-9]/                 # Router configuration directories
    ├── frr.conf            # FRR routing configuration
    ├── daemons             # FRR daemon configuration
    └── vtysh.conf          # vtysh configuration
```

## License

This tool is part of the final IP project.
