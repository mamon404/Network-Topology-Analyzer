#!/usr/bin/env python3
"""
Network Topology Visualizer
"""

import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import networkx as nx
from jinja2 import Template

class NetworkVisualizer:
    def __init__(self, topology_data):
        self.topology = topology_data
        self.graph = topology_data['graph']
        self.hierarchy = topology_data['hierarchy']
        self.devices = topology_data['devices']
        self.links = topology_data['links']
    
    def generate_json_output(self, output_file):
        """Generate JSON output"""
        json_data = {
            'topology': {
                'devices': self._devices_to_json(),
                'links': self.links,
                'hierarchy': self.hierarchy,
                'statistics': self.topology['statistics']
            },
            'generated_by': 'Network Topology Generator',
            'timestamp': self._get_timestamp()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"📄 JSON output saved: {output_file}")
    
    def generate_html_report(self, output_file):
        """Generate HTML report"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Network Topology Report</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .device { background-color: #f8f9fa; margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; }
        .link { background-color: #e9ecef; margin: 10px 0; padding: 10px; border-left: 4px solid #28a745; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .stat-box { background-color: #17a2b8; color: white; padding: 15px; text-align: center; border-radius: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Network Topology Report</h1>
        <p>Generated on: {{ timestamp }}</p>
    </div>
    
    <div class="section">
        <h2>📊 Network Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <h3>{{ stats.total_devices }}</h3>
                <p>Total Devices</p>
            </div>
            <div class="stat-box">
                <h3>{{ stats.total_links }}</h3>
                <p>Total Links</p>
            </div>
            <div class="stat-box">
                <h3>{{ stats.ospf_areas }}</h3>
                <p>OSPF Areas</p>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🏗️ Network Hierarchy</h2>
        
        <h3>Core Layer ({{ hierarchy.core|length }} devices)</h3>
        {% for device in hierarchy.core %}
            <div class="device">
                <strong>{{ device }}</strong> - Core Router
            </div>
        {% endfor %}
        
        <h3>Distribution Layer ({{ hierarchy.distribution|length }} devices)</h3>
        {% for device in hierarchy.distribution %}
            <div class="device">
                <strong>{{ device }}</strong> - Distribution Device
            </div>
        {% endfor %}
        
        <h3>Access Layer ({{ hierarchy.access|length }} devices)</h3>
        {% for device in hierarchy.access %}
            <div class="device">
                <strong>{{ device }}</strong> - Access Switch
            </div>
        {% endfor %}
    </div>
    
    <div class="section">
        <h2>📡 Network Links</h2>
        <table>
            <tr>
                <th>Source</th>
                <th>Target</th>
                <th>Bandwidth</th>
                <th>Utilization</th>
                <th>Link Type</th>
            </tr>
            {% for link in links %}
            <tr>
                <td>{{ link.source }}</td>
                <td>{{ link.target }}</td>
                <td>{{ link.bandwidth }}</td>
                <td>{{ link.utilization }}</td>
                <td>{{ link.link_type }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    
    <div class="section">
        <h2>🔧 Device Details</h2>
        {% for device in devices %}
        <div class="device">
            <h4>{{ device.hostname }} ({{ device.device_type|title }})</h4>
            <p><strong>Interfaces:</strong></p>
            <ul>
            {% for intf_name, intf in device.interfaces.items() %}
                <li>{{ intf_name }} - {{ intf.ip_address or 'No IP' }} ({{ intf.bandwidth }})</li>
            {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
    
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(
            timestamp=self._get_timestamp(),
            stats=self.topology['statistics'],
            hierarchy=self.hierarchy,
            links=self.links,
            devices=self.devices
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"🌐 HTML report saved: {output_file}")
    
    def generate_network_diagram(self, output_file):
        """Generate network diagram"""
        try:
            plt.figure(figsize=(12, 8))
            
            # Create layout based on hierarchy
            pos = self._create_hierarchical_layout()
            
            # Check if we have any nodes to draw
            if not self.graph.nodes():
                print("ℹ️  No network nodes to visualize")
                return
            
            # Draw nodes by hierarchy
            self._draw_hierarchical_nodes(pos)
            
            # Draw edges with bandwidth labels
            self._draw_edges_with_bandwidth(pos)
            
            plt.title('Network Topology - Hierarchical View', size=16, fontweight='bold')
            plt.axis('off')
            plt.tight_layout()
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"🎨 Network diagram saved: {output_file}")
            
        except Exception as e:
            print(f"❌ Error generating network diagram: {e}")
            print("ℹ️  Continuing without network diagram...")
    
    def _create_hierarchical_layout(self):
        """Create hierarchical layout positions"""
        pos = {}
        
        # Core layer (top)
        core_devices = self.hierarchy.get('core', [])
        if core_devices:
            for i, device in enumerate(core_devices):
                x_pos = (i * 2) - (len(core_devices) - 1)
                pos[device] = (x_pos, 3)
        
        # Distribution layer (middle)  
        dist_devices = self.hierarchy.get('distribution', [])
        if dist_devices:
            for i, device in enumerate(dist_devices):
                x_pos = (i * 2) - (len(dist_devices) - 1)
                pos[device] = (x_pos, 2)
        
        # Access layer (bottom)
        access_devices = self.hierarchy.get('access', [])
        if access_devices:
            for i, device in enumerate(access_devices):
                x_pos = (i * 2) - (len(access_devices) - 1)
                pos[device] = (x_pos, 1)
        
        # If no hierarchical positions, use spring layout
        if not pos:
            pos = nx.spring_layout(self.graph)
        
        return pos
    
    def _draw_hierarchical_nodes(self, pos):
        """Draw nodes by hierarchy level"""
        # Core devices (red)
        core_devices = self.hierarchy.get('core', [])
        if core_devices:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=core_devices, 
                                  node_color='red', node_size=1500, alpha=0.8)
        
        # Distribution devices (orange)
        dist_devices = self.hierarchy.get('distribution', [])
        if dist_devices:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=dist_devices, 
                                  node_color='orange', node_size=1200, alpha=0.8)
        
        # Access devices (lightblue)
        access_devices = self.hierarchy.get('access', [])
        if access_devices:
            nx.draw_networkx_nodes(self.graph, pos, nodelist=access_devices, 
                                  node_color='lightblue', node_size=1000, alpha=0.8)
        
        # Add labels
        if self.graph.nodes():
            nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold')
    
    def _draw_edges_with_bandwidth(self, pos):
        """Draw edges with bandwidth information - FIXED VERSION"""
        if not self.graph.edges():
            return
            
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, alpha=0.6, width=2)
        
        # Add bandwidth labels - Safe approach
        edge_labels = {}
        try:
            # Method 1: Try with data=True
            for u, v, data in self.graph.edges(data=True):
                if isinstance(data, dict):
                    bandwidth = data.get('bandwidth', '100Mbps')
                else:
                    bandwidth = '100Mbps'
                edge_labels[(u, v)] = bandwidth
                
        except Exception:
            try:
                # Method 2: Fallback - iterate without data
                for edge in self.graph.edges():
                    if len(edge) >= 2:
                        edge_data = self.graph.get_edge_data(edge[0], edge[1])
                        if edge_data and isinstance(edge_data, dict):
                            bandwidth = edge_data.get('bandwidth', '100Mbps')
                        else:
                            bandwidth = '100Mbps'
                        edge_labels[(edge[0], edge[1])] = bandwidth
            except Exception:
                # Method 3: Ultimate fallback
                for edge in self.graph.edges():
                    edge_labels[(edge, edge[1])] = '100Mbps'
        
        # Draw edge labels if any exist
        if edge_labels:
            try:
                nx.draw_networkx_edge_labels(self.graph, pos, edge_labels, font_size=8)
            except Exception as e:
                print(f"Warning: Could not draw edge labels: {e}")
    
    def _devices_to_json(self):
        """Convert devices to JSON format"""
        json_devices = []
        for device in self.devices:
            json_devices.append({
                'hostname': device.get('hostname', 'Unknown'),
                'type': device.get('device_type', 'Unknown'),
                'interfaces': device.get('interfaces', {}),
                'ospf_info': device.get('ospf_info', {}),
                'networks': device.get('ip_networks', [])
            })
        return json_devices
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
