#!/usr/bin/env python3
"""
Standalone Network Topology Visualizer
Generates a network diagram and saves it to a file (no GUI required)
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import sys


def create_topology_visualization(output_file='network_topology.png'):
    """Create and save network topology visualization"""
    
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
    
    # Add routers with IP info
    routers = ['r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9']
    for router in routers:
        G.add_node(router, node_type='router', ip=node_ips[router])
    
    # Add hosts with IP info
    hosts = ['pc1', 'pc2', 'pc3', 'pc4']
    for host in hosts:
        G.add_node(host, node_type='host', ip=node_ips[host])
    
    # Add links
    links = [
        {'src': 'r1', 'dst': 'r2', 'type': 'RIP'},
        {'src': 'r2', 'dst': 'r3', 'type': 'RIP'},
        {'src': 'r2', 'dst': 'r4', 'type': 'BGP'},
        {'src': 'r4', 'dst': 'r5', 'type': 'OSPF'},
        {'src': 'r5', 'dst': 'r6', 'type': 'OSPF'},
        {'src': 'r6', 'dst': 'r7', 'type': 'BGP'},
        {'src': 'r7', 'dst': 'r8', 'type': 'OSPF'},
        {'src': 'r7', 'dst': 'r9', 'type': 'OSPF'},
        {'src': 'r2', 'dst': 'r7', 'type': 'Peering'},
        {'src': 'pc1', 'dst': 'r1', 'type': 'Host'},
        {'src': 'pc2', 'dst': 'r3', 'type': 'Host'},
        {'src': 'pc3', 'dst': 'r8', 'type': 'Host'},
        {'src': 'pc4', 'dst': 'r9', 'type': 'Host'}
    ]
    
    for link in links:
        G.add_edge(link['src'], link['dst'], link_type=link['type'])
    
    # Create figure
    fig, ax = plt.subplots(figsize=(16, 10))
    
    # Define custom positions based on AS topology
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
            'igp': 'OSPF',
            'label_position': 'right'  # Label on right
        },
        'ISP #1\n(AS 200)': {
            'xy': (0.2, 0.2),
            'width': 5.6,
            'height': 4.6,
            'color': '#E6F3FF',
            'edge_color': '#4A90E2',
            'igp': 'RIP',
            'label_position': 'left'  # Label on left
        },
        'ISP #2\n(AS 300)': {
            'xy': (6.2, 0.2),
            'width': 3.6,
            'height': 4.6,
            'color': '#E6FFE6',
            'edge_color': '#4CAF50',
            'igp': 'OSPF',
            'label_position': 'right'  # Label on right
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
    
    # Save to file
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Network topology saved to: {output_file}")
    
    # Also save as PDF
    pdf_file = output_file.replace('.png', '.pdf')
    plt.savefig(pdf_file, bbox_inches='tight', facecolor='white')
    print(f"✅ Network topology saved to: {pdf_file}")
    
    plt.close()


if __name__ == '__main__':
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'network_topology.png'
    
    try:
        create_topology_visualization(output_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
