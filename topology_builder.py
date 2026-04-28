#!/usr/bin/env python3
"""
Network Topology Builder
"""

import networkx as nx

class TopologyBuilder:
    def __init__(self, devices_data):
        self.devices_data = devices_data
        self.graph = nx.Graph()
        self.hierarchy = {'core': [], 'distribution': [], 'access': []}
    
    def build_hierarchical_topology(self):
        """Build complete network topology"""
        # Add devices to graph
        self._add_devices_to_graph()
        
        # Detect connections
        self._detect_connections()
        
        # Classify hierarchy
        self._classify_hierarchy()
        
        # Add bandwidth information
        self._add_bandwidth_info()
        
        return {
            'graph': self.graph,
            'hierarchy': self.hierarchy,
            'devices': self.devices_data,
            'links': self._get_links(),
            'statistics': self._generate_statistics()
        }
    
    def _add_devices_to_graph(self):
        """Add devices as nodes to graph"""
        for device in self.devices_data:
            self.graph.add_node(
                device['hostname'],
                device_type=device['device_type'],
                interfaces=device['interfaces'],
                ospf_info=device.get('ospf_info', {}),
                networks=device.get('ip_networks', [])
            )
    
    def _detect_connections(self):
        """Detect connections between devices"""
        devices = list(self.graph.nodes())
        
        for i, device1 in enumerate(devices):
            for device2 in devices[i+1:]:
                if self._are_connected(device1, device2):
                    connection_info = self._get_connection_info(device1, device2)
                    self.graph.add_edge(device1, device2, **connection_info)
    
    def _are_connected(self, device1, device2):
        """Check if two devices are connected"""
        device1_data = self.graph.nodes[device1]
        device2_data = self.graph.nodes[device2]
        
        # Check for common subnets
        for intf1_name, intf1 in device1_data['interfaces'].items():
            if not intf1.get('ip_address'):
                continue
                
            for intf2_name, intf2 in device2_data['interfaces'].items():
                if not intf2.get('ip_address'):
                    continue
                
                if self._same_subnet(intf1['ip_address'], intf1.get('subnet_mask'), 
                                   intf2['ip_address'], intf2.get('subnet_mask')):
                    return True
        
        return False
    
    def _same_subnet(self, ip1, mask1, ip2, mask2):
        """Check if two IPs are in same subnet"""
        try:
            import ipaddress
            if mask1 and mask2:
                net1 = ipaddress.IPv4Network(f"{ip1}/{mask1}", strict=False)
                net2 = ipaddress.IPv4Network(f"{ip2}/{mask2}", strict=False)
                return net1.network_address == net2.network_address
        except:
            pass
        return False
    
    def _get_connection_info(self, device1, device2):
        """Get connection information between devices"""
        device1_data = self.graph.nodes[device1]
        device2_data = self.graph.nodes[device2]
        
        connection_info = {
            'link_type': 'ethernet',
            'bandwidth': '100Mbps',  # Default
            'utilization': '0%',
            'interfaces': []
        }
        
        # Find connected interfaces
        for intf1_name, intf1 in device1_data['interfaces'].items():
            for intf2_name, intf2 in device2_data['interfaces'].items():
                if (intf1.get('ip_address') and intf2.get('ip_address') and 
                    self._same_subnet(intf1['ip_address'], intf1.get('subnet_mask'),
                                     intf2['ip_address'], intf2.get('subnet_mask'))):
                    
                    connection_info['interfaces'] = [
                        {'device': device1, 'interface': intf1_name, 'ip': intf1['ip_address']},
                        {'device': device2, 'interface': intf2_name, 'ip': intf2['ip_address']}
                    ]
                    connection_info['bandwidth'] = min(intf1.get('bandwidth', '100Mbps'), 
                                                     intf2.get('bandwidth', '100Mbps'))
                    break
        
        return connection_info
    
    def _classify_hierarchy(self):
        """Classify devices into hierarchical layers"""
        for device_name in self.graph.nodes():
            device_data = self.graph.nodes[device_name]
            device_type = device_data['device_type']
            
            # Simple classification based on device type and connections
            if device_type == 'router':
                if len(list(self.graph.neighbors(device_name))) >= 2:
                    self.hierarchy['core'].append(device_name)
                else:
                    self.hierarchy['distribution'].append(device_name)
            
            elif device_type == 'switch':
                self.hierarchy['access'].append(device_name)
            
            else:
                self.hierarchy['access'].append(device_name)
    
    def _add_bandwidth_info(self):
        """Add bandwidth information to topology"""
        for edge in self.graph.edges():
            edge_data = self.graph.edges[edge]
            if 'bandwidth' not in edge_data:
                edge_data['bandwidth'] = '100Mbps'
            if 'utilization' not in edge_data:
                edge_data['utilization'] = '0%'
    
    def _get_links(self):
        """Get all links in the topology"""
        links = []
        for edge in self.graph.edges(data=True):
            link_info = {
                'source': edge[0],
                'target': edge[1],
                'bandwidth': edge[2].get('bandwidth', '100Mbps'),
                'utilization': edge[2].get('utilization', '0%'),
                'link_type': edge[2].get('link_type', 'ethernet'),
                'interfaces': edge[2].get('interfaces', [])
            }
            links.append(link_info)
        return links
    
    def _generate_statistics(self):
        """Generate topology statistics"""
        return {
            'total_devices': len(self.graph.nodes()),
            'total_links': len(self.graph.edges()),
            'core_devices': len(self.hierarchy['core']),
            'distribution_devices': len(self.hierarchy['distribution']),
            'access_devices': len(self.hierarchy['access']),
            'ospf_areas': self._count_ospf_areas()
        }
    
    def _count_ospf_areas(self):
        """Count OSPF areas"""
        areas = set()
        for device_name in self.graph.nodes():
            device_data = self.graph.nodes[device_name]
            ospf_info = device_data.get('ospf_info', {})
            if 'networks' in ospf_info:
                for network in ospf_info['networks']:
                    areas.add(network.get('area', '0'))
        return len(areas)
