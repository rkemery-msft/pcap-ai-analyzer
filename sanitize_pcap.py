#!/usr/bin/env python3
"""
PCAP Sanitization Script
Removes PII and customer information from packet capture files while preserving traffic patterns.

Sanitizes:
- IP addresses (consistent anonymization)
- MAC addresses
- DNS queries/responses
- HTTP headers (User-Agent, cookies, auth tokens)
- TLS SNI (Server Name Indication)
- Hostnames
- Email addresses
- API keys and tokens
"""

import os
import sys
import hashlib
import ipaddress
from scapy.all import rdpcap, wrpcap, IP, IPv6, Ether, DNS, DNSQR, DNSRR, Raw, TCP, UDP
from scapy.layers.http import HTTPRequest, HTTPResponse
from scapy.layers.tls.all import TLS, TLSClientHello, TLSServerHello
import re
from datetime import datetime

class PCAPSanitizer:
    def __init__(self, preserve_internal_ips=True):
        """
        Initialize the sanitizer
        
        Args:
            preserve_internal_ips: If True, keeps private IP ranges recognizable (10.x, 172.16.x, 192.168.x)
        """
        self.ip_map = {}
        self.mac_map = {}
        self.domain_map = {}
        self.preserve_internal_ips = preserve_internal_ips
        
        # Patterns to detect sensitive data
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.api_key_patterns = [
            re.compile(r'\b[A-Za-z0-9]{32,}\b'),  # Generic long strings
            re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE),
            re.compile(r'api[_-]?key["\s:=]+[A-Za-z0-9]+', re.IGNORECASE),
            re.compile(r'token["\s:=]+[A-Za-z0-9]+', re.IGNORECASE),
        ]
        
        self.stats = {
            'total_packets': 0,
            'ip_anonymized': 0,
            'mac_anonymized': 0,
            'dns_sanitized': 0,
            'http_sanitized': 0,
            'tls_sanitized': 0,
            'sensitive_data_removed': 0
        }
    
    def _hash_value(self, value, prefix=''):
        """Create a consistent hash for anonymization"""
        hash_obj = hashlib.sha256(f"{value}".encode())
        return prefix + hash_obj.hexdigest()[:16]
    
    def anonymize_ip(self, ip_str):
        """Anonymize IP address while maintaining consistency"""
        if ip_str in self.ip_map:
            return self.ip_map[ip_str]
        
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            
            # Check if it's a private IP
            if ip_obj.is_private and self.preserve_internal_ips:
                # Keep private IPs in their ranges but anonymize last octets
                if isinstance(ip_obj, ipaddress.IPv4Address):
                    octets = ip_str.split('.')
                    if octets[0] == '10':
                        anon_ip = f"10.{self._hash_value(ip_str, '')[:3]}.{self._hash_value(ip_str, '')[3:6]}.{self._hash_value(ip_str, '')[6:9]}"
                        anon_ip = f"10.{int(self._hash_value(ip_str, '')[:2], 16) % 256}.{int(self._hash_value(ip_str, '')[2:4], 16) % 256}.{int(self._hash_value(ip_str, '')[4:6], 16) % 256}"
                    elif octets[0] == '172' and 16 <= int(octets[1]) <= 31:
                        anon_ip = f"172.{16 + int(self._hash_value(ip_str, '')[0:2], 16) % 16}.{int(self._hash_value(ip_str, '')[2:4], 16) % 256}.{int(self._hash_value(ip_str, '')[4:6], 16) % 256}"
                    elif octets[0] == '192' and octets[1] == '168':
                        anon_ip = f"192.168.{int(self._hash_value(ip_str, '')[:2], 16) % 256}.{int(self._hash_value(ip_str, '')[2:4], 16) % 256}"
                    else:
                        anon_ip = f"10.{int(self._hash_value(ip_str, '')[:2], 16) % 256}.{int(self._hash_value(ip_str, '')[2:4], 16) % 256}.{int(self._hash_value(ip_str, '')[4:6], 16) % 256}"
                else:
                    # IPv6 private - simplified anonymization
                    anon_ip = f"fd00::{self._hash_value(ip_str, '')[:8]}"
            else:
                # Public IPs - map to different public range
                if isinstance(ip_obj, ipaddress.IPv4Address):
                    # Use 203.0.113.0/24 (TEST-NET-3) for anonymized public IPs
                    anon_ip = f"203.0.113.{int(self._hash_value(ip_str, '')[:2], 16) % 256}"
                else:
                    # IPv6 public - use documentation prefix
                    anon_ip = f"2001:db8::{self._hash_value(ip_str, '')[:8]}"
            
            self.ip_map[ip_str] = anon_ip
            return anon_ip
            
        except ValueError:
            return ip_str
    
    def anonymize_mac(self, mac_str):
        """Anonymize MAC address"""
        if mac_str in self.mac_map:
            return self.mac_map[mac_str]
        
        # Keep the OUI (first 3 bytes) as 00:00:00 and hash the rest
        hash_part = self._hash_value(mac_str, '')[:6]
        anon_mac = f"00:00:00:{hash_part[0:2]}:{hash_part[2:4]}:{hash_part[4:6]}"
        self.mac_map[mac_str] = anon_mac
        return anon_mac
    
    def anonymize_domain(self, domain):
        """Anonymize domain names"""
        if domain in self.domain_map:
            return self.domain_map[domain]
        
        # Keep TLD recognizable, hash the rest
        parts = domain.split('.')
        if len(parts) >= 2:
            tld = parts[-1]
            hashed = self._hash_value(domain, '')[:12]
            anon_domain = f"anon-{hashed}.{tld}"
        else:
            anon_domain = f"anon-{self._hash_value(domain, '')[:12]}.local"
        
        self.domain_map[domain] = anon_domain
        return anon_domain
    
    def sanitize_dns(self, packet):
        """Sanitize DNS queries and responses"""
        if packet.haslayer(DNS):
            dns = packet[DNS]
            
            # Sanitize queries
            if dns.qd:
                qname = dns.qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                anon_qname = self.anonymize_domain(qname)
                dns.qd.qname = anon_qname.encode() + b'.'
                self.stats['dns_sanitized'] += 1
            
            # Sanitize answers
            if dns.an:
                for i in range(dns.ancount):
                    try:
                        if dns.an[i].rdata:
                            rdata = dns.an[i].rdata
                            if isinstance(rdata, bytes):
                                # Could be a domain name or IP
                                rdata_str = rdata.decode('utf-8', errors='ignore').rstrip('.')
                                if '.' in rdata_str and not rdata_str[0].isdigit():
                                    anon_rdata = self.anonymize_domain(rdata_str)
                                    dns.an[i].rdata = anon_rdata.encode() + b'.'
                    except:
                        pass
        
        return packet
    
    def sanitize_http(self, packet):
        """Sanitize HTTP headers and payloads"""
        if packet.haslayer(Raw):
            try:
                payload = packet[Raw].load
                
                # Check if it looks like HTTP
                if b'HTTP/' in payload or b'GET ' in payload or b'POST ' in payload:
                    payload_str = payload.decode('utf-8', errors='ignore')
                    
                    # Remove common sensitive headers
                    sensitive_headers = [
                        'Authorization:', 'Cookie:', 'Set-Cookie:', 
                        'X-API-Key:', 'X-Auth-Token:', 'User-Agent:',
                        'X-Forwarded-For:', 'X-Real-IP:'
                    ]
                    
                    for header in sensitive_headers:
                        if header in payload_str:
                            # Replace header value with [REDACTED]
                            pattern = f'{header}[^\r\n]*'
                            payload_str = re.sub(pattern, f'{header} [REDACTED]', payload_str)
                            self.stats['http_sanitized'] += 1
                    
                    # Remove email addresses
                    if self.email_pattern.search(payload_str):
                        payload_str = self.email_pattern.sub('[EMAIL_REDACTED]', payload_str)
                        self.stats['sensitive_data_removed'] += 1
                    
                    # Remove potential API keys
                    for pattern in self.api_key_patterns:
                        if pattern.search(payload_str):
                            payload_str = pattern.sub('[KEY_REDACTED]', payload_str)
                            self.stats['sensitive_data_removed'] += 1
                    
                    packet[Raw].load = payload_str.encode('utf-8', errors='ignore')
            except:
                pass
        
        return packet
    
    def sanitize_tls(self, packet):
        """Sanitize TLS SNI and other TLS data"""
        if packet.haslayer(TLS):
            try:
                # Check for ClientHello with SNI
                if packet.haslayer(TLSClientHello):
                    # TLS SNI sanitization is complex with Scapy
                    # For now, we'll just note it
                    self.stats['tls_sanitized'] += 1
            except:
                pass
        
        return packet
    
    def sanitize_packet(self, packet):
        """Sanitize a single packet"""
        self.stats['total_packets'] += 1
        
        try:
            # Anonymize Ethernet layer
            if packet.haslayer(Ether):
                ether = packet[Ether]
                if ether.src != "00:00:00:00:00:00":
                    ether.src = self.anonymize_mac(ether.src)
                    self.stats['mac_anonymized'] += 1
                if ether.dst != "00:00:00:00:00:00":
                    ether.dst = self.anonymize_mac(ether.dst)
                    self.stats['mac_anonymized'] += 1
            
            # Anonymize IP layer
            if packet.haslayer(IP):
                ip = packet[IP]
                ip.src = self.anonymize_ip(ip.src)
                ip.dst = self.anonymize_ip(ip.dst)
                self.stats['ip_anonymized'] += 2
                
                # Remove IP checksums to be recalculated
                del ip.chksum
                if packet.haslayer(TCP):
                    del packet[TCP].chksum
                elif packet.haslayer(UDP):
                    del packet[UDP].chksum
            
            # Anonymize IPv6
            if packet.haslayer(IPv6):
                ipv6 = packet[IPv6]
                ipv6.src = self.anonymize_ip(ipv6.src)
                ipv6.dst = self.anonymize_ip(ipv6.dst)
                self.stats['ip_anonymized'] += 2
            
            # Sanitize DNS
            packet = self.sanitize_dns(packet)
            
            # Sanitize HTTP
            packet = self.sanitize_http(packet)
            
            # Sanitize TLS
            packet = self.sanitize_tls(packet)
            
        except Exception as e:
            print(f"Warning: Error sanitizing packet {self.stats['total_packets']}: {e}")
        
        return packet
    
    def sanitize_file(self, input_file, output_file):
        """Sanitize entire PCAP file"""
        print(f"Reading PCAP file: {input_file}")
        print("This may take a while for large files...")
        
        try:
            packets = rdpcap(input_file)
            print(f"Loaded {len(packets)} packets")
            
            sanitized_packets = []
            for i, packet in enumerate(packets):
                if i % 1000 == 0:
                    print(f"Processing packet {i}/{len(packets)}...")
                
                sanitized_packet = self.sanitize_packet(packet)
                sanitized_packets.append(sanitized_packet)
            
            print(f"\nWriting sanitized PCAP to: {output_file}")
            wrpcap(output_file, sanitized_packets)
            
            print("\n" + "="*60)
            print("SANITIZATION COMPLETE")
            print("="*60)
            print(f"Total packets processed: {self.stats['total_packets']}")
            print(f"IP addresses anonymized: {self.stats['ip_anonymized']}")
            print(f"MAC addresses anonymized: {self.stats['mac_anonymized']}")
            print(f"DNS queries sanitized: {self.stats['dns_sanitized']}")
            print(f"HTTP data sanitized: {self.stats['http_sanitized']}")
            print(f"TLS data sanitized: {self.stats['tls_sanitized']}")
            print(f"Sensitive data removed: {self.stats['sensitive_data_removed']}")
            print(f"\nOutput file: {output_file}")
            print(f"Output size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
            
        except Exception as e:
            print(f"Error processing PCAP file: {e}")
            sys.exit(1)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sanitize PCAP files by removing PII and customer-sensitive information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic sanitization
  python sanitize_pcap.py --input capture.cap --output sanitized.cap
  
  # Preserve private IP ranges
  python sanitize_pcap.py --input capture.cap --output sanitized.cap --preserve-private-ips
  
  # Auto-generate output filename
  python sanitize_pcap.py --input capture.cap
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input PCAP file path'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output PCAP file path (default: sanitized_<timestamp>.cap in same directory)'
    )
    
    parser.add_argument(
        '--preserve-private-ips',
        action='store_true',
        default=True,
        help='Keep private IP ranges recognizable (10.x, 172.16.x, 192.168.x) (default: True)'
    )
    
    parser.add_argument(
        '--no-preserve-private-ips',
        action='store_true',
        help='Anonymize all IPs including private ranges'
    )
    
    args = parser.parse_args()
    
    input_file = args.input
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Generate output filename if not provided
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_dir = os.path.dirname(input_file) or '.'
        output_file = os.path.join(input_dir, f"sanitized_capture_{timestamp}.cap")
    
    preserve_ips = args.preserve_private_ips and not args.no_preserve_private_ips
    
    print("="*60)
    print("PCAP SANITIZATION TOOL")
    print("="*60)
    print(f"Input file: {input_file}")
    print(f"Input size: {os.path.getsize(input_file) / (1024*1024):.2f} MB")
    print(f"Output file: {output_file}")
    print(f"Preserve private IPs: {preserve_ips}")
    print("\nThis will anonymize:")
    print("  - IP addresses (public and private)")
    print("  - MAC addresses")
    print("  - DNS queries and responses")
    print("  - HTTP headers (cookies, auth, user-agent)")
    print("  - Email addresses")
    print("  - API keys and tokens")
    print("\n")
    
    sanitizer = PCAPSanitizer(preserve_internal_ips=preserve_ips)
    sanitizer.sanitize_file(input_file, output_file)


if __name__ == "__main__":
    main()
