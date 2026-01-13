#!/usr/bin/env python3
"""
Network Topology Visualizer and Editor
A native GUI tool to visualize and edit the Mininet network topology
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import re
from pathlib import Path
import subprocess


class TopologyEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Topology Editor")
        self.root.geometry("1400x900")
        
        # Data structures
        self.topology_data = self.load_topology()
        
        # Create UI
        self.create_ui()
        
        # Load initial data
        self.refresh_topology_view()
    
    def create_ui(self):
        """Create the main UI layout"""
        # Create main paned window
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Topology tree view
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        
        # Right panel - Details and editor
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=2)
        
        self.create_left_panel(left_frame)
        self.create_right_panel(right_frame)
    
    def create_left_panel(self, parent):
        """Create the left panel with topology tree"""
        # Title
        title = ttk.Label(parent, text="Network Topology", font=('Arial', 14, 'bold'))
        title.pack(pady=5)
        
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Refresh", command=self.refresh_topology_view).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Visualize", command=self.visualize_topology).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export", command=self.export_topology).pack(side=tk.LEFT, padx=2)
        
        # Tree view
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(tree_frame, 
                                 yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set,
                                 selectmode='browse')
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Configure columns
        self.tree['columns'] = ('value', 'type')
        self.tree.column('#0', width=200, minwidth=150)
        self.tree.column('value', width=200, minwidth=150)
        self.tree.column('type', width=100, minwidth=80)
        
        self.tree.heading('#0', text='Name')
        self.tree.heading('value', text='Value')
        self.tree.heading('type', text='Type')
    
    def create_right_panel(self, parent):
        """Create the right panel with details and editor"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Details View
        details_frame = ttk.Frame(self.notebook)
        self.notebook.add(details_frame, text='Details')
        self.create_details_tab(details_frame)
        
        # Tab 2: Configuration Editor
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text='Configuration')
        self.create_config_tab(config_frame)
        
        # Tab 3: Network Diagram
        diagram_frame = ttk.Frame(self.notebook)
        self.notebook.add(diagram_frame, text='Network Diagram')
        self.create_diagram_tab(diagram_frame)
    
    def create_details_tab(self, parent):
        """Create the details view tab"""
        # Title
        self.details_title = ttk.Label(parent, text="Select an item", font=('Arial', 12, 'bold'))
        self.details_title.pack(pady=10)
        
        # Details text area
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.details_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                      font=('Courier', 10))
        self.details_text.pack(fill=tk.BOTH, expand=True)
    
    def create_config_tab(self, parent):
        """Create the configuration editor tab"""
        # Router selector
        selector_frame = ttk.Frame(parent)
        selector_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(selector_frame, text="Router:").pack(side=tk.LEFT, padx=5)
        self.router_var = tk.StringVar()
        self.router_combo = ttk.Combobox(selector_frame, textvariable=self.router_var,
                                         values=['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9'],
                                         state='readonly')
        self.router_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.router_combo.bind('<<ComboboxSelected>>', self.load_router_config)
        
        # Config type selector
        ttk.Label(selector_frame, text="Config:").pack(side=tk.LEFT, padx=5)
        self.config_type_var = tk.StringVar(value="frr.conf")
        config_combo = ttk.Combobox(selector_frame, textvariable=self.config_type_var,
                                   values=['frr.conf', 'daemons', 'vtysh.conf'],
                                   state='readonly', width=15)
        config_combo.pack(side=tk.LEFT, padx=5)
        config_combo.bind('<<ComboboxSelected>>', self.load_router_config)
        
        # Toolbar
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(toolbar, text="Save", command=self.save_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Reload", command=self.load_router_config).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Validate", command=self.validate_config).pack(side=tk.LEFT, padx=2)
        
        # Config editor
        editor_frame = ttk.Frame(parent)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.config_editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.NONE,
                                                       font=('Courier', 10))
        self.config_editor.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.config_status = ttk.Label(parent, text="Ready", relief=tk.SUNKEN)
        self.config_status.pack(fill=tk.X, padx=10, pady=5)
    
    def create_diagram_tab(self, parent):
        """Create the network diagram tab"""
        # Info text
        info_text = """
Network Topology Diagram

Autonomous Systems:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────────┐
│                              Tier 1 (AS 100)                            │
│                                                                         │
│                    R4 ────────── R5 ────────── R6                       │
│                    │            OSPF            │                       │
│                    │                            │                       │
└────────────────────┼────────────────────────────┼─────────────────────────┘
                     │                            │
                   BGP                          BGP
                     │                            │
┌────────────────────┼────────────────────────────┼─────────────────────────┐
│                    │                            │                         │
│  ISP #1 (AS 200)   │                            │      ISP #2 (AS 300)    │
│                    │                            │                         │
│   R1 ─── R2 ─── R3 │                            │  R7 ─── R8              │
│   │      │      │  │                            │  │      │               │
│   │     RIP     │  │                            │  │     OSPF             │
│   │             │  │                            │  │                      │
│  PC1           PC2 │                            │  │                      │
│                    │                            │  R9                     │
│                    └────────── Peering ─────────┘  │                      │
│                                                    PC3                    │
│                                                    PC4                    │
└─────────────────────────────────────────────────────────────────────────┘

IP Addressing:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Router Links (10.0.X.0/24):
  • R1-R2:  10.0.1.0/24
  • R2-R3:  10.0.2.0/24
  • R2-R4:  10.0.3.0/24 (BGP)
  • R4-R5:  10.0.4.0/24
  • R5-R6:  10.0.5.0/24
  • R6-R7:  10.0.6.0/24 (BGP)
  • R7-R8:  10.0.7.0/24
  • R7-R9:  10.0.8.0/24
  • R2-R7:  10.0.9.0/24 (Peering)

Host Networks (192.168.X.0/24):
  • PC1: 192.168.1.0/24 (on R1)
  • PC2: 192.168.2.0/24 (on R3)
  • PC3: 192.168.3.0/24 (on R8)
  • PC4: 192.168.4.0/24 (on R9)

Routing Protocols:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • ISP #1 (AS 200): RIP
  • Tier 1 (AS 100): OSPF
  • ISP #2 (AS 300): OSPF
  • Inter-AS: BGP
        """
        
        text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD, 
                                                font=('Courier', 9))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert('1.0', info_text)
        text_widget.config(state=tk.DISABLED)
    
    def load_topology(self):
        """Load topology data from topology.py and config files"""
        topology = {
            'routers': {},
            'hosts': {},
            'links': [],
            'as_info': {
                'AS 100': {'routers': ['r4', 'r5', 'r6'], 'igp': 'OSPF'},
                'AS 200': {'routers': ['r1', 'r2', 'r3'], 'igp': 'RIP'},
                'AS 300': {'routers': ['r7', 'r8', 'r9'], 'igp': 'OSPF'}
            }
        }
        
        # Define routers
        routers = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9']
        for router in routers:
            topology['routers'][router] = {
                'interfaces': [],
                'config_files': {
                    'frr.conf': f'{router}/frr.conf',
                    'daemons': f'{router}/daemons',
                    'vtysh.conf': f'{router}/vtysh.conf'
                }
            }
        
        # Define hosts
        hosts = {
            'pc1': {'ip': '192.168.1.2/24', 'gateway': '192.168.1.1', 'router': 'r1'},
            'pc2': {'ip': '192.168.2.2/24', 'gateway': '192.168.2.1', 'router': 'r3'},
            'pc3': {'ip': '192.168.3.2/24', 'gateway': '192.168.3.1', 'router': 'r8'},
            'pc4': {'ip': '192.168.4.2/24', 'gateway': '192.168.4.1', 'router': 'r9'}
        }
        topology['hosts'] = hosts
        
        # Define links
        links = [
            {'src': 'r1', 'dst': 'r2', 'src_ip': '10.0.1.1/24', 'dst_ip': '10.0.1.2/24', 'type': 'RIP'},
            {'src': 'r2', 'dst': 'r3', 'src_ip': '10.0.2.1/24', 'dst_ip': '10.0.2.2/24', 'type': 'RIP'},
            {'src': 'r2', 'dst': 'r4', 'src_ip': '10.0.3.1/24', 'dst_ip': '10.0.3.2/24', 'type': 'BGP'},
            {'src': 'r4', 'dst': 'r5', 'src_ip': '10.0.4.1/24', 'dst_ip': '10.0.4.2/24', 'type': 'OSPF'},
            {'src': 'r5', 'dst': 'r6', 'src_ip': '10.0.5.1/24', 'dst_ip': '10.0.5.2/24', 'type': 'OSPF'},
            {'src': 'r6', 'dst': 'r7', 'src_ip': '10.0.6.1/24', 'dst_ip': '10.0.6.2/24', 'type': 'BGP'},
            {'src': 'r7', 'dst': 'r8', 'src_ip': '10.0.7.1/24', 'dst_ip': '10.0.7.2/24', 'type': 'OSPF'},
            {'src': 'r7', 'dst': 'r9', 'src_ip': '10.0.8.1/24', 'dst_ip': '10.0.8.2/24', 'type': 'OSPF'},
            {'src': 'r2', 'dst': 'r7', 'src_ip': '10.0.9.1/24', 'dst_ip': '10.0.9.2/24', 'type': 'Peering'},
            {'src': 'pc1', 'dst': 'r1', 'src_ip': '192.168.1.2/24', 'dst_ip': '192.168.1.1/24', 'type': 'Host'},
            {'src': 'pc2', 'dst': 'r3', 'src_ip': '192.168.2.2/24', 'dst_ip': '192.168.2.1/24', 'type': 'Host'},
            {'src': 'pc3', 'dst': 'r8', 'src_ip': '192.168.3.2/24', 'dst_ip': '192.168.3.1/24', 'type': 'Host'},
            {'src': 'pc4', 'dst': 'r9', 'src_ip': '192.168.4.2/24', 'dst_ip': '192.168.4.1/24', 'type': 'Host'}
        ]
        topology['links'] = links
        
        return topology
    
    def refresh_topology_view(self):
        """Refresh the topology tree view"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add AS sections
        for as_name, as_data in self.topology_data['as_info'].items():
            as_node = self.tree.insert('', 'end', text=as_name, 
                                       values=(as_data['igp'], 'AS'),
                                       tags=('as',))
            
            # Add routers in this AS
            for router in as_data['routers']:
                router_node = self.tree.insert(as_node, 'end', text=router,
                                              values=('Router', 'Device'),
                                              tags=('router',))
                
                # Add interfaces
                interfaces = [link for link in self.topology_data['links'] 
                            if link['src'] == router or link['dst'] == router]
                
                if interfaces:
                    intf_node = self.tree.insert(router_node, 'end', text='Interfaces',
                                                values=(f'{len(interfaces)} links', 'Group'))
                    for link in interfaces:
                        if link['src'] == router:
                            link_text = f"to {link['dst']}"
                            link_ip = link['src_ip']
                        else:
                            link_text = f"to {link['src']}"
                            link_ip = link['dst_ip']
                        
                        self.tree.insert(intf_node, 'end', text=link_text,
                                       values=(link_ip, link['type']))
        
        # Add hosts section
        hosts_node = self.tree.insert('', 'end', text='Hosts',
                                     values=(f"{len(self.topology_data['hosts'])} hosts", 'Group'),
                                     tags=('hosts',))
        
        for host_name, host_data in self.topology_data['hosts'].items():
            host_node = self.tree.insert(hosts_node, 'end', text=host_name,
                                        values=(host_data['ip'], 'Host'),
                                        tags=('host',))
            self.tree.insert(host_node, 'end', text='Gateway',
                           values=(host_data['gateway'], 'Config'))
            self.tree.insert(host_node, 'end', text='Router',
                           values=(host_data['router'], 'Config'))
        
        # Expand all
        self.expand_all(self.tree)
    
    def expand_all(self, tree, item=''):
        """Expand all tree items"""
        children = tree.get_children(item)
        for child in children:
            tree.item(child, open=True)
            self.expand_all(tree, child)
    
    def on_tree_select(self, event):
        """Handle tree selection event"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        item_text = self.tree.item(item, 'text')
        item_values = self.tree.item(item, 'values')
        
        # Update details view
        self.details_title.config(text=f"Details: {item_text}")
        
        details = f"Name: {item_text}\n"
        if item_values:
            details += f"Value: {item_values[0]}\n"
            details += f"Type: {item_values[1]}\n"
        
        # If it's a router, show more details
        if item_text in self.topology_data['routers']:
            details += f"\n{'='*60}\n"
            details += f"Router Configuration Files:\n"
            details += f"{'='*60}\n"
            for config_type, config_path in self.topology_data['routers'][item_text]['config_files'].items():
                details += f"  • {config_type}: {config_path}\n"
            
            # Show links
            links = [link for link in self.topology_data['links'] 
                    if link['src'] == item_text or link['dst'] == item_text]
            if links:
                details += f"\n{'='*60}\n"
                details += f"Connected Links:\n"
                details += f"{'='*60}\n"
                for link in links:
                    if link['src'] == item_text:
                        details += f"  • {item_text} ({link['src_ip']}) → {link['dst']} ({link['dst_ip']}) [{link['type']}]\n"
                    else:
                        details += f"  • {link['src']} ({link['src_ip']}) → {item_text} ({link['dst_ip']}) [{link['type']}]\n"
        
        self.details_text.delete('1.0', tk.END)
        self.details_text.insert('1.0', details)
    
    def load_router_config(self, event=None):
        """Load router configuration file"""
        router = self.router_var.get()
        config_type = self.config_type_var.get()
        
        if not router:
            return
        
        config_path = Path(f"{router}/{config_type}")
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                
                self.config_editor.delete('1.0', tk.END)
                self.config_editor.insert('1.0', content)
                self.config_status.config(text=f"Loaded: {config_path}")
            else:
                self.config_status.config(text=f"File not found: {config_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {str(e)}")
            self.config_status.config(text=f"Error loading file")
    
    def save_config(self):
        """Save router configuration file"""
        router = self.router_var.get()
        config_type = self.config_type_var.get()
        
        if not router:
            messagebox.showwarning("Warning", "Please select a router first")
            return
        
        config_path = Path(f"{router}/{config_type}")
        
        try:
            content = self.config_editor.get('1.0', tk.END)
            
            # Backup original file
            if config_path.exists():
                backup_path = config_path.with_suffix(config_path.suffix + '.bak')
                config_path.rename(backup_path)
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            self.config_status.config(text=f"Saved: {config_path}")
            messagebox.showinfo("Success", f"Configuration saved to {config_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
            self.config_status.config(text=f"Error saving file")
    
    def validate_config(self):
        """Validate FRR configuration"""
        router = self.router_var.get()
        config_type = self.config_type_var.get()
        
        if not router or config_type != 'frr.conf':
            messagebox.showinfo("Info", "Validation is only available for frr.conf files")
            return
        
        content = self.config_editor.get('1.0', tk.END)
        
        # Basic validation
        issues = []
        
        # Check for required sections
        if 'hostname' not in content:
            issues.append("Missing 'hostname' directive")
        
        # Check for proper line endings
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('!') and not line.startswith('#'):
                # Check for common issues
                if line.endswith(','):
                    issues.append(f"Line {i}: Unexpected comma at end of line")
        
        if issues:
            result = "Validation Issues Found:\n\n" + "\n".join(f"• {issue}" for issue in issues)
            messagebox.showwarning("Validation", result)
        else:
            messagebox.showinfo("Validation", "Configuration looks good!")
    
    def visualize_topology(self):
        """Create a visual graph of the topology using matplotlib with AS-based clustering"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            import networkx as nx
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            messagebox.showerror("Error", 
                               "matplotlib and networkx are required for visualization.\n"
                               "Install with: pip install matplotlib networkx")
            return
        
        # Create new window
        viz_window = tk.Toplevel(self.root)
        viz_window.title("Network Topology Visualization")
        viz_window.geometry("1400x900")
        
        # Create graph
        G = nx.Graph()
        
        # Define IP addresses for each node (primary management IP)
        node_ips = {
            # Routers - using their router-id or primary interface
            'r1': '10.0.1.1',
            'r2': '10.0.1.2',
            'r3': '10.0.2.2',
            'r4': '10.0.3.2',
            'r5': '10.0.4.2',
            'r6': '10.0.5.2',
            'r7': '10.0.6.2',
            'r8': '10.0.7.2',
            'r9': '10.0.8.2',
            # Hosts
            'pc1': '192.168.1.2',
            'pc2': '192.168.2.2',
            'pc3': '192.168.3.2',
            'pc4': '192.168.4.2'
        }
        
        # Add nodes with IP info
        for router in self.topology_data['routers']:
            G.add_node(router, node_type='router', ip=node_ips[router])
        
        for host in self.topology_data['hosts']:
            G.add_node(host, node_type='host', ip=node_ips[host])
        
        # Add edges
        for link in self.topology_data['links']:
            G.add_edge(link['src'], link['dst'], 
                      link_type=link['type'],
                      src_ip=link.get('src_ip', ''),
                      dst_ip=link.get('dst_ip', ''))
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Define custom positions based on AS topology (similar to reference image)
        pos = {
            # Tier 1 (AS 100) - Top center
            'r4': (2, 8),
            'r5': (5, 8),
            'r6': (8, 8),
            
            # ISP #1 (AS 200) - Bottom left
            'r1': (1, 3),
            'r2': (3, 4),
            'r3': (5, 3),
            'pc1': (1, 1),
            'pc2': (5, 1),
            
            # ISP #2 (AS 300) - Bottom right
            'r7': (8, 4),
            'r8': (7, 3),
            'r9': (9, 3),
            'pc3': (7, 1),
            'pc4': (9, 1),
        }
        
        # Define AS boundaries for visual grouping
        as_boxes = {
            'Tier 1\n(AS 100)': {
                'xy': (1.2, 6.8),
                'width': 7.6,
                'height': 2.0,
                'color': '#FFE6E6',
                'edge_color': '#FF6B6B',
                'routers': ['r4', 'r5', 'r6'],
                'igp': 'OSPF',
                'label_position': 'right'
            },
            'ISP #1\n(AS 200)': {
                'xy': (0.2, 0.2),
                'width': 5.6,
                'height': 4.6,
                'color': '#E6F3FF',
                'edge_color': '#4A90E2',
                'routers': ['r1', 'r2', 'r3'],
                'igp': 'RIP',
                'label_position': 'left'
            },
            'ISP #2\n(AS 300)': {
                'xy': (6.2, 0.2),
                'width': 3.6,
                'height': 4.6,
                'color': '#E6FFE6',
                'edge_color': '#4CAF50',
                'routers': ['r7', 'r8', 'r9'],
                'igp': 'OSPF',
                'label_position': 'right'
            }
        }
        
        # Draw AS boundary boxes
        for as_name, box_info in as_boxes.items():
            rect = mpatches.FancyBboxPatch(
                box_info['xy'], box_info['width'], box_info['height'],
                boxstyle="round,pad=0.1",
                linewidth=2,
                edgecolor=box_info['edge_color'],
                facecolor=box_info['color'],
                alpha=0.3,
                linestyle='--'
            )
            ax.add_patch(rect)
            
            # Position label based on label_position
            if box_info['label_position'] == 'left':
                label_x = box_info['xy'][0] + box_info['width'] * 0.15
            else:  # right
                label_x = box_info['xy'][0] + box_info['width'] * 0.85
            
            label_y = box_info['xy'][1] + box_info['height'] * 0.85
            ax.text(label_x, label_y, as_name,
                   fontsize=11, fontweight='bold',
                   color=box_info['edge_color'],
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                           edgecolor=box_info['edge_color'], linewidth=1.5))
            
            # Add IGP label
            igp_y = box_info['xy'][1] + box_info['height'] * 0.15
            ax.text(label_x, igp_y, f"IGP: {box_info['igp']}",
                   fontsize=9, style='italic',
                   color=box_info['edge_color'],
                   ha='center', va='center')
        
        # Separate nodes by type
        routers = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'router']
        hosts = [n for n, d in G.nodes(data=True) if d.get('node_type') == 'host']
        
        # Draw edges with different colors and styles based on type
        edge_styles = {
            'RIP': {'color': '#4A90E2', 'width': 2.5, 'style': 'solid', 'alpha': 0.7},
            'OSPF': {'color': '#4CAF50', 'width': 2.5, 'style': 'solid', 'alpha': 0.7},
            'BGP': {'color': '#FF6B6B', 'width': 3.5, 'style': 'solid', 'alpha': 0.9},
            'Peering': {'color': '#9C27B0', 'width': 3.0, 'style': 'dashed', 'alpha': 0.8},
            'Host': {'color': '#757575', 'width': 2.0, 'style': 'solid', 'alpha': 0.5}
        }
        
        for link_type, style in edge_styles.items():
            edges = [(u, v) for u, v, d in G.edges(data=True) 
                    if d.get('link_type') == link_type]
            if edges:
                nx.draw_networkx_edges(G, pos, edgelist=edges,
                                      edge_color=style['color'],
                                      width=style['width'],
                                      style=style['style'],
                                      alpha=style['alpha'],
                                      ax=ax)
        
        # Draw router nodes
        nx.draw_networkx_nodes(G, pos, nodelist=routers, 
                              node_color='white',
                              edgecolors='#333333',
                              linewidths=2.5,
                              node_size=2500, 
                              node_shape='s',
                              ax=ax)
        
        # Draw host nodes
        nx.draw_networkx_nodes(G, pos, nodelist=hosts,
                              node_color='#B2DFDB',
                              edgecolors='#00796B',
                              linewidths=2,
                              node_size=2000,
                              node_shape='o',
                              ax=ax)
        
        # Draw node labels with names
        nx.draw_networkx_labels(G, pos, font_size=11, font_weight='bold',
                               font_family='sans-serif', ax=ax)
        
        # Draw IP addresses below each node
        ip_labels = {node: node_ips[node] for node in G.nodes()}
        ip_pos = {node: (x, y - 0.35) for node, (x, y) in pos.items()}
        
        for node, (x, y) in ip_pos.items():
            ax.text(x, y, ip_labels[node],
                   fontsize=8,
                   ha='center', va='top',
                   color='#555555',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                            edgecolor='none', alpha=0.8))
        
        # Create custom legend
        legend_elements = [
            mpatches.Patch(facecolor='white', edgecolor='#333333', linewidth=2, label='Routers'),
            mpatches.Patch(facecolor='#B2DFDB', edgecolor='#00796B', linewidth=2, label='Hosts'),
            mpatches.Patch(facecolor='none', edgecolor='#4A90E2', linewidth=2.5, label='RIP'),
            mpatches.Patch(facecolor='none', edgecolor='#4CAF50', linewidth=2.5, label='OSPF'),
            mpatches.Patch(facecolor='none', edgecolor='#FF6B6B', linewidth=3.5, label='BGP'),
            mpatches.Patch(facecolor='none', edgecolor='#9C27B0', linewidth=3, 
                          linestyle='--', label='Peering'),
            mpatches.Patch(facecolor='none', edgecolor='#757575', linewidth=2, label='Host Link')
        ]
        
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10,
                 framealpha=0.9, edgecolor='black')
        
        ax.set_title("Multi-AS Network Topology", fontsize=18, fontweight='bold', pad=20)
        ax.set_xlim(-0.5, 10.5)
        ax.set_ylim(-0.5, 9.5)
        ax.axis('off')
        
        plt.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=viz_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar_frame = ttk.Frame(viz_window)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar_frame, text="Save Image", 
                  command=lambda: self.save_visualization(fig)).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text="Close", 
                  command=viz_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def save_visualization(self, fig):
        """Save the visualization to a file"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if filename:
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Success", f"Visualization saved to {filename}")
    
    def export_topology(self):
        """Export topology data to JSON"""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.topology_data, f, indent=2)
                messagebox.showinfo("Success", f"Topology exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")


def main():
    root = tk.Tk()
    app = TopologyEditor(root)
    root.mainloop()


if __name__ == '__main__':
    main()
