#!/usr/bin/env python3
"""
Simple Network Configuration Parser
"""

import re

class NetworkConfigParser:
    def __init__(self):
        self.device_data = {}
    
    def parse_config(self, config_file):
        """Parse router/switch configuration"""
        with open(config_file, 'r') as f:
            config_content = f.read()
        
        device_info = {
            'hostname': self._extract_hostname(config_content),
            'device_type': self._detect_device_type(config_content),
            'interfaces': self._parse_interfaces(config_content),
            'ospf_info': self._parse_ospf(config_content),
            'ip_networks': self._extract_networks(config_content)
        }
        
        return device_info
    
    def _extract_hostname(self, config):
        """Extract device hostname"""
        match = re.search(r'hostname\s+(\S+)', config)
        return match.group(1) if match else 'Unknown'
    
    def _detect_device_type(self, config):
        """Detect if router or switch"""
        if 'router ospf' in config.lower():
            return 'router'
        elif 'switchport' in config.lower():
            return 'switch'
        return 'unknown'
    
    def _parse_interfaces(self, config):
        """Parse interface configurations"""
        interfaces = {}
        
        # Find all interfaces
        intf_blocks = re.findall(r'interface\s+(\S+)(.*?)(?=interface|\Z)', config, re.DOTALL | re.IGNORECASE)
        
        for intf_name, intf_config in intf_blocks:
            interface_data = {
                'name': intf_name,
                'ip_address': None,
                'subnet_mask': None,
                'description': None,
                'bandwidth': self._get_bandwidth(intf_name),
                'status': 'up'
            }
            
            # Extract IP address
            ip_match = re.search(r'ip address\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)', intf_config)
            if ip_match:
                interface_data['ip_address'] = ip_match.group(1)
                interface_data['subnet_mask'] = ip_match.group(2)
            
            # Extract description
            desc_match = re.search(r'description\s+(.+)', intf_config)
            if desc_match:
                interface_data['description'] = desc_match.group(1).strip()
            
            interfaces[intf_name] = interface_data
        
        return interfaces
    
    def _get_bandwidth(self, interface_name):
        """Get interface bandwidth based on type"""
        if 'gigabit' in interface_name.lower():
            return '1Gbps'
        elif 'fastethernet' in interface_name.lower():
            return '100Mbps'
        elif 'serial' in interface_name.lower():
            return '1.544Mbps'
        return '10Mbps'
    
    def _parse_ospf(self, config):
        """Parse OSPF configuration"""
        ospf_info = {}
        
        # Find OSPF process
        ospf_match = re.search(r'router ospf\s+(\d+)', config, re.IGNORECASE)
        if ospf_match:
            ospf_info['process_id'] = ospf_match.group(1)
            
            # Find router ID
            rid_match = re.search(r'router-id\s+(\d+\.\d+\.\d+\.\d+)', config)
            if rid_match:
                ospf_info['router_id'] = rid_match.group(1)
            
            # Find networks
            networks = re.findall(r'network\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+area\s+(\d+)', config)
            ospf_info['networks'] = [{'network': n[0], 'wildcard': n[1], 'area': n[2]} for n in networks]
        
        return ospf_info
    
    def _extract_networks(self, config):
        """Extract all IP networks"""
        networks = []
        
        # Find all IP addresses
        ip_addresses = re.findall(r'ip address\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)', config)
        
        for ip, mask in ip_addresses:
            networks.append({
                'ip': ip,
                'mask': mask,
                'network': self._calculate_network(ip, mask)
            })
        
        return networks
    
    def _calculate_network(self, ip, mask):
        """Calculate network address"""
        try:
            import ipaddress
            network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
            return str(network.network_address)
        except:
            return ip
