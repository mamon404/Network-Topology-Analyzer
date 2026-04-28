#!/usr/bin/env python3
"""
Network Topology Generation - Main Application
"""

import json
import os
from config_parser import NetworkConfigParser
from topology_builder import TopologyBuilder
from network_visualizer import NetworkVisualizer

def main():
    print("🌐 Network Topology Generator Started...")
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Configuration files path
    config_files = [
        'sample_configs/Router1.txt',
        # 'sample_configs/Router11.txt',
        'sample_configs/Router2.txt',
        # 'sample_configs/Router22.txt',
        'sample_configs/Router3.txt',
        # 'sample_configs/Router33.txt',s
        'sample_configs/Switch1.txt',
        # 'sample_configs/Switch11.txt',
        'sample_configs/Switch2.txt'
        # 'sample_configs/Switch22.txt'
    ]
    
    # Parse configurations
    parser = NetworkConfigParser()
    all_devices = []
    
    for config_file in config_files:
        try:
            device_data = parser.parse_config(config_file)
            all_devices.append(device_data)
            print(f"✅ Parsed: {device_data['hostname']}")
        except Exception as e:
            print(f"❌ Error parsing {config_file}: {e}")
            continue
    
    if not all_devices:
        print("❌ No devices parsed successfully!")
        return
    
    # Build topology
    builder = TopologyBuilder(all_devices)
    topology = builder.build_hierarchical_topology()
    
    # Generate visualizations
    visualizer = NetworkVisualizer(topology)
    
    try:
        # Create outputs
        visualizer.generate_json_output('output/topology.json')
        visualizer.generate_html_report('output/topology.html')
        visualizer.generate_network_diagram('output/network_diagram.png')
        
        print("🎉 Topology Generation Complete!")
        print("📁 Check output/ folder for results")
        
    except Exception as e:
        print(f"❌ Error generating outputs: {e}")

if __name__ == "__main__":
    main()
