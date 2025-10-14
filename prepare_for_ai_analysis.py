#!/usr/bin/env python3
"""
PCAP to AI-Optimized Analysis Format
Converts packet capture files into structured, token-efficient formats for AI analysis.

This script extracts and organizes PCAP data into digestible chunks that are:
- Token-efficient (removes redundancy)
- Structured (JSON/Markdown formats)
- Contextual (groups related packets)
- Prioritized (focuses on errors and anomalies)

Perfect for feeding to Azure OpenAI GPT-5 models or other LLMs for troubleshooting.
"""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict, Counter
from scapy.all import rdpcap, IP, IPv6, TCP, UDP, DNS, DNSQR, DNSRR, Raw, ICMP
import hashlib

class PCAPAnalysisPrep:
    def __init__(self, pcap_file):
        self.pcap_file = pcap_file
        self.packets = []
        self.stats = {
            'total_packets': 0,
            'protocols': Counter(),
            'src_ips': Counter(),
            'dst_ips': Counter(),
            'src_ports': Counter(),
            'dst_ports': Counter(),
            'tcp_flags': Counter(),
            'dns_queries': Counter(),
            'dns_failures': [],
            'http_errors': [],
            'tcp_retransmissions': [],
            'tcp_resets': [],
            'connection_failures': [],
            'large_packets': [],
            'errors_by_type': defaultdict(list),
            'conversations': defaultdict(lambda: {
                'packets': 0,
                'bytes': 0,
                'first_seen': None,
                'last_seen': None,
                'flags': []
            })
        }
        self.tcp_seq_track = defaultdict(set)  # Track TCP sequences for retransmission detection
        
    def load_packets(self):
        """Load packets from PCAP file with comprehensive error handling"""
        print(f"Loading PCAP file: {self.pcap_file}")
        
        try:
            # Validate file before attempting to read
            if not os.path.exists(self.pcap_file):
                raise FileNotFoundError(f"PCAP file not found: {self.pcap_file}")
            
            if not os.access(self.pcap_file, os.R_OK):
                raise PermissionError(f"Cannot read PCAP file: {self.pcap_file}")
            
            # Attempt to read PCAP
            self.packets = rdpcap(self.pcap_file)
            self.stats['total_packets'] = len(self.packets)
            
            if len(self.packets) == 0:
                raise ValueError("PCAP file contains no packets")
            
            print(f"✓ Loaded {len(self.packets):,} packets")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"PCAP file not found: {self.pcap_file}") from e
        except PermissionError as e:
            raise PermissionError(f"Cannot read PCAP file (permission denied): {self.pcap_file}") from e
        except ValueError as e:
            if "Not a supported capture file" in str(e) or "unknown file format" in str(e):
                raise ValueError(f"Invalid or corrupted PCAP file format: {self.pcap_file}") from e
            raise
        except MemoryError:
            raise MemoryError(f"File too large to load into memory: {self.pcap_file}") from None
        except Exception as e:
            # Catch any other scapy-related errors
            error_msg = str(e).lower()
            if "truncated" in error_msg or "premature end" in error_msg:
                raise ValueError(f"Corrupted or truncated PCAP file: {self.pcap_file}") from e
            elif "permission" in error_msg:
                raise PermissionError(f"Cannot read PCAP file: {self.pcap_file}") from e
            else:
                raise RuntimeError(f"Failed to load PCAP file: {e}") from e
    
    def analyze_packet(self, pkt, pkt_num):
        """Analyze a single packet for errors and anomalies"""
        timestamp = float(pkt.time)
        
        # Protocol identification
        if pkt.haslayer(IP):
            ip = pkt[IP]
            self.stats['protocols']['IPv4'] += 1
            self.stats['src_ips'][ip.src] += 1
            self.stats['dst_ips'][ip.dst] += 1
            
            # Track conversation
            if pkt.haslayer(TCP):
                tcp = pkt[TCP]
                conv_key = f"{ip.src}:{tcp.sport} -> {ip.dst}:{tcp.dport}"
                conv = self.stats['conversations'][conv_key]
                conv['packets'] += 1
                conv['bytes'] += len(pkt)
                if conv['first_seen'] is None:
                    conv['first_seen'] = timestamp
                conv['last_seen'] = timestamp
                conv['flags'].append(tcp.flags)
                
                self.stats['protocols']['TCP'] += 1
                self.stats['src_ports'][tcp.sport] += 1
                self.stats['dst_ports'][tcp.dport] += 1
                
                # TCP flags analysis
                flags = []
                if tcp.flags.S: flags.append('SYN')
                if tcp.flags.A: flags.append('ACK')
                if tcp.flags.F: flags.append('FIN')
                if tcp.flags.R: flags.append('RST')
                if tcp.flags.P: flags.append('PSH')
                
                flag_str = '|'.join(flags) if flags else 'NONE'
                self.stats['tcp_flags'][flag_str] += 1
                
                # Detect TCP resets (connection issues)
                if tcp.flags.R:
                    self.stats['tcp_resets'].append({
                        'packet_num': pkt_num,
                        'timestamp': timestamp,
                        'src': f"{ip.src}:{tcp.sport}",
                        'dst': f"{ip.dst}:{tcp.dport}",
                        'seq': tcp.seq,
                        'ack': tcp.ack
                    })
                    self.stats['errors_by_type']['TCP_RESET'].append(pkt_num)
                
                # Detect retransmissions
                conn_key = f"{ip.src}:{tcp.sport}->{ip.dst}:{tcp.dport}"
                seq_key = f"{tcp.seq}-{len(pkt)}"
                if seq_key in self.tcp_seq_track[conn_key] and len(pkt) > 60:
                    self.stats['tcp_retransmissions'].append({
                        'packet_num': pkt_num,
                        'timestamp': timestamp,
                        'src': f"{ip.src}:{tcp.sport}",
                        'dst': f"{ip.dst}:{tcp.dport}",
                        'seq': tcp.seq,
                        'length': len(pkt)
                    })
                    self.stats['errors_by_type']['TCP_RETRANSMISSION'].append(pkt_num)
                else:
                    self.tcp_seq_track[conn_key].add(seq_key)
                
                # Detect SYN without SYN-ACK response (connection failures)
                if tcp.flags.S and not tcp.flags.A:
                    self.stats['connection_failures'].append({
                        'packet_num': pkt_num,
                        'timestamp': timestamp,
                        'src': f"{ip.src}:{tcp.sport}",
                        'dst': f"{ip.dst}:{tcp.dport}",
                        'type': 'SYN_NO_RESPONSE'
                    })
                
            elif pkt.haslayer(UDP):
                udp = pkt[UDP]
                self.stats['protocols']['UDP'] += 1
                self.stats['src_ports'][udp.sport] += 1
                self.stats['dst_ports'][udp.dport] += 1
                
                conv_key = f"{ip.src}:{udp.sport} -> {ip.dst}:{udp.dport}"
                conv = self.stats['conversations'][conv_key]
                conv['packets'] += 1
                conv['bytes'] += len(pkt)
                if conv['first_seen'] is None:
                    conv['first_seen'] = timestamp
                conv['last_seen'] = timestamp
            
            elif pkt.haslayer(ICMP):
                icmp = pkt[ICMP]
                self.stats['protocols']['ICMP'] += 1
                
                # ICMP errors are important
                if icmp.type == 3:  # Destination Unreachable
                    self.stats['errors_by_type']['ICMP_DEST_UNREACHABLE'].append({
                        'packet_num': pkt_num,
                        'timestamp': timestamp,
                        'src': ip.src,
                        'dst': ip.dst,
                        'code': icmp.code
                    })
        
        elif pkt.haslayer(IPv6):
            self.stats['protocols']['IPv6'] += 1
        
        # DNS Analysis
        if pkt.haslayer(DNS):
            dns = pkt[DNS]
            if dns.qr == 0:  # Query
                if dns.qd:
                    qname = dns.qd.qname.decode('utf-8', errors='ignore').rstrip('.')
                    self.stats['dns_queries'][qname] += 1
            else:  # Response
                if dns.rcode != 0:  # DNS error
                    qname = dns.qd.qname.decode('utf-8', errors='ignore').rstrip('.') if dns.qd else 'unknown'
                    self.stats['dns_failures'].append({
                        'packet_num': pkt_num,
                        'timestamp': timestamp,
                        'query': qname,
                        'rcode': dns.rcode,
                        'rcode_name': self._dns_rcode_name(dns.rcode)
                    })
                    self.stats['errors_by_type']['DNS_FAILURE'].append(pkt_num)
        
        # HTTP Error Detection
        if pkt.haslayer(Raw):
            try:
                payload = pkt[Raw].load.decode('utf-8', errors='ignore')
                
                # HTTP error codes
                if 'HTTP/' in payload:
                    for error_code in ['400', '401', '403', '404', '500', '502', '503', '504']:
                        if f'HTTP/1.1 {error_code}' in payload or f'HTTP/1.0 {error_code}' in payload:
                            self.stats['http_errors'].append({
                                'packet_num': pkt_num,
                                'timestamp': timestamp,
                                'src': f"{pkt[IP].src}:{pkt[TCP].sport}" if pkt.haslayer(IP) and pkt.haslayer(TCP) else 'unknown',
                                'dst': f"{pkt[IP].dst}:{pkt[TCP].dport}" if pkt.haslayer(IP) and pkt.haslayer(TCP) else 'unknown',
                                'status_code': error_code,
                                'preview': payload[:200]
                            })
                            self.stats['errors_by_type'][f'HTTP_{error_code}'].append(pkt_num)
                            break
            except:
                pass
        
        # Large packet detection (fragmentation issues)
        if len(pkt) > 1400:
            self.stats['large_packets'].append({
                'packet_num': pkt_num,
                'timestamp': timestamp,
                'size': len(pkt),
                'src': pkt[IP].src if pkt.haslayer(IP) else 'unknown',
                'dst': pkt[IP].dst if pkt.haslayer(IP) else 'unknown'
            })
    
    def _dns_rcode_name(self, rcode):
        """Convert DNS rcode to name"""
        rcodes = {
            0: 'NOERROR',
            1: 'FORMERR',
            2: 'SERVFAIL',
            3: 'NXDOMAIN',
            4: 'NOTIMP',
            5: 'REFUSED'
        }
        return rcodes.get(rcode, f'UNKNOWN({rcode})')
    
    def analyze_all(self):
        """Analyze all packets"""
        print("Analyzing packets for errors and anomalies...")
        for i, pkt in enumerate(self.packets):
            if i % 5000 == 0 and i > 0:
                print(f"  Processed {i}/{len(self.packets)} packets...")
            self.analyze_packet(pkt, i + 1)
        print(f"Analysis complete: {len(self.packets)} packets processed")
    
    def generate_summary(self):
        """Generate executive summary optimized for AI"""
        summary = {
            'metadata': {
                'source_file': os.path.basename(self.pcap_file),
                'total_packets': self.stats['total_packets'],
                'analysis_timestamp': datetime.now().isoformat(),
                'file_size_mb': os.path.getsize(self.pcap_file) / (1024*1024)
            },
            'protocol_distribution': dict(self.stats['protocols'].most_common()),
            'top_sources': [{'ip': ip, 'packets': count} for ip, count in self.stats['src_ips'].most_common(10)],
            'top_destinations': [{'ip': ip, 'packets': count} for ip, count in self.stats['dst_ips'].most_common(10)],
            'top_ports': {
                'source': [{'port': port, 'packets': count} for port, count in self.stats['src_ports'].most_common(10)],
                'destination': [{'port': port, 'packets': count} for port, count in self.stats['dst_ports'].most_common(10)]
            },
            'tcp_flags_distribution': dict(self.stats['tcp_flags'].most_common(10)),
            'error_summary': {
                'total_errors': sum(len(v) if isinstance(v, list) else 0 for v in self.stats['errors_by_type'].values()),
                'error_types': {k: len(v) if isinstance(v, list) else 0 for k, v in self.stats['errors_by_type'].items()},
                'tcp_resets': len(self.stats['tcp_resets']),
                'tcp_retransmissions': len(self.stats['tcp_retransmissions']),
                'dns_failures': len(self.stats['dns_failures']),
                'http_errors': len(self.stats['http_errors']),
                'connection_failures': len(self.stats['connection_failures'])
            },
            'top_dns_queries': [{'domain': domain, 'count': count} for domain, count in self.stats['dns_queries'].most_common(20)]
        }
        return summary
    
    def generate_error_details(self):
        """Generate detailed error information"""
        return {
            'tcp_resets': self.stats['tcp_resets'][:50],  # Limit to first 50
            'tcp_retransmissions': self.stats['tcp_retransmissions'][:50],
            'dns_failures': self.stats['dns_failures'][:50],
            'http_errors': self.stats['http_errors'][:50],
            'connection_failures': self.stats['connection_failures'][:30],
            'large_packets': self.stats['large_packets'][:20]
        }
    
    def generate_conversation_summary(self):
        """Summarize top conversations"""
        conversations = []
        for conv_key, conv_data in sorted(
            self.stats['conversations'].items(),
            key=lambda x: x[1]['packets'],
            reverse=True
        )[:20]:  # Top 20 conversations
            duration = conv_data['last_seen'] - conv_data['first_seen'] if conv_data['first_seen'] else 0
            
            # Convert flags to JSON-serializable format
            flags_counter = Counter()
            for flag in conv_data['flags']:
                # Convert FlagValue to string
                flags_counter[str(flag)] += 1
            
            conversations.append({
                'conversation': conv_key,
                'packets': conv_data['packets'],
                'bytes': conv_data['bytes'],
                'duration_seconds': round(duration, 3),
                'flags_summary': [{'flag': flag, 'count': count} for flag, count in flags_counter.most_common(5)]
            })
        return conversations
    
    def generate_ai_prompt_template(self, summary, errors, conversations):
        """Generate a ready-to-use AI prompt"""
        prompt = f"""# Network Traffic Analysis Request

## Context
I need help analyzing a network packet capture from an Azure AKS escalation. The capture has been sanitized and analyzed for errors and anomalies.

## Summary Statistics
- **Total Packets**: {summary['metadata']['total_packets']:,}
- **File Size**: {summary['metadata']['file_size_mb']:.2f} MB
- **Capture Source**: {summary['metadata']['source_file']}

### Protocol Distribution
{json.dumps(summary['protocol_distribution'], indent=2)}

### Top Error Counts
- TCP Resets: {summary['error_summary']['tcp_resets']}
- TCP Retransmissions: {summary['error_summary']['tcp_retransmissions']}
- DNS Failures: {summary['error_summary']['dns_failures']}
- HTTP Errors: {summary['error_summary']['http_errors']}
- Connection Failures: {summary['error_summary']['connection_failures']}

## Top Traffic Sources
{json.dumps(summary['top_sources'][:5], indent=2)}

## Top Traffic Destinations
{json.dumps(summary['top_destinations'][:5], indent=2)}

## Top Destination Ports (Indicating Services)
{json.dumps(summary['top_ports']['destination'][:10], indent=2)}

## Critical Errors Detected

### TCP Resets (Connection Terminations)
```json
{json.dumps(errors['tcp_resets'][:10], indent=2)}
```

### TCP Retransmissions (Network Issues)
```json
{json.dumps(errors['tcp_retransmissions'][:10], indent=2)}
```

### DNS Failures
```json
{json.dumps(errors['dns_failures'][:10], indent=2)}
```

### HTTP Errors
```json
{json.dumps(errors['http_errors'][:5], indent=2)}
```

## Top Network Conversations
{json.dumps(conversations[:10], indent=2)}

## Analysis Questions

Based on this network capture data, please analyze:

1. **Root Cause**: What appears to be the primary issue causing errors in this traffic?
2. **Error Pattern**: Is there a pattern to the TCP resets, retransmissions, or connection failures?
3. **Service Impact**: Which services or endpoints are most affected?
4. **Network Path**: Do the errors suggest client-side, network, or server-side issues?
5. **DNS Issues**: Are there DNS resolution problems contributing to the failures?
6. **Recommendations**: What specific steps should be taken to resolve these issues?

Please provide:
- A concise root cause analysis
- Specific evidence from the packet data
- Prioritized troubleshooting steps
- Any Azure/AKS-specific considerations
"""
        return prompt
    
    def export_analysis(self, output_dir):
        """Export all analysis data in AI-optimized formats"""
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\nGenerating AI-optimized analysis files...")
        
        # Generate data
        summary = self.generate_summary()
        errors = self.generate_error_details()
        conversations = self.generate_conversation_summary()
        
        # 1. Executive Summary (JSON) - Most compact
        summary_file = os.path.join(output_dir, 'summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Created: {summary_file}")
        
        # 2. Error Details (JSON)
        errors_file = os.path.join(output_dir, 'errors_detailed.json')
        with open(errors_file, 'w') as f:
            json.dump(errors, f, indent=2)
        print(f"✓ Created: {errors_file}")
        
        # 3. Conversations (JSON)
        conv_file = os.path.join(output_dir, 'conversations.json')
        with open(conv_file, 'w') as f:
            json.dump(conversations, f, indent=2)
        print(f"✓ Created: {conv_file}")
        
        # 4. AI Prompt Template (Markdown) - Ready to paste
        prompt = self.generate_ai_prompt_template(summary, errors, conversations)
        prompt_file = os.path.join(output_dir, 'ai_analysis_prompt.md')
        with open(prompt_file, 'w') as f:
            f.write(prompt)
        print(f"✓ Created: {prompt_file}")
        
        # 5. Quick Stats (Text) - Human readable
        stats_file = os.path.join(output_dir, 'quick_stats.txt')
        with open(stats_file, 'w') as f:
            f.write("PCAP ANALYSIS - QUICK STATS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Packets: {summary['metadata']['total_packets']:,}\n")
            f.write(f"File Size: {summary['metadata']['file_size_mb']:.2f} MB\n")
            f.write(f"\nERRORS FOUND:\n")
            f.write(f"  TCP Resets: {summary['error_summary']['tcp_resets']}\n")
            f.write(f"  Retransmissions: {summary['error_summary']['tcp_retransmissions']}\n")
            f.write(f"  DNS Failures: {summary['error_summary']['dns_failures']}\n")
            f.write(f"  HTTP Errors: {summary['error_summary']['http_errors']}\n")
            f.write(f"  Connection Failures: {summary['error_summary']['connection_failures']}\n")
            f.write(f"\nPROTOCOLS:\n")
            for proto, count in summary['protocol_distribution'].items():
                f.write(f"  {proto}: {count:,}\n")
            f.write(f"\nTOP DESTINATIONS:\n")
            for dest in summary['top_destinations'][:5]:
                f.write(f"  {dest['ip']}: {dest['packets']:,} packets\n")
        print(f"✓ Created: {stats_file}")
        
        # 6. Token estimate
        total_tokens = self._estimate_tokens(prompt)
        token_file = os.path.join(output_dir, 'token_estimate.txt')
        with open(token_file, 'w') as f:
            f.write("TOKEN USAGE ESTIMATE FOR AI ANALYSIS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"AI Prompt Template Tokens: ~{total_tokens:,}\n")
            f.write(f"Expected Output Tokens: ~{int(total_tokens * 0.6):,}\n\n")
            f.write(f"Estimated Cost (Azure OpenAI GPT-5-chat - Global Deployment):\n")
            f.write(f"  gpt-5-chat:  ${((total_tokens * 1.25 / 1_000_000) + (total_tokens * 0.6 * 10.00 / 1_000_000)):.4f}\n")
            f.write(f"\nPricing (per 1M tokens):\n")
            f.write(f"  gpt-5-chat: $1.25 input / $10.00 output (recommended)\n")
            f.write(f"\nSee: https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/\n")
            f.write(f"\nOptimization: ✓ Reduced from ~{summary['metadata']['file_size_mb']:.0f}MB to ~{total_tokens:,} tokens\n")
            f.write(f"Compression Ratio: ~{(summary['metadata']['file_size_mb'] * 1024 * 1024 * 2.5) / total_tokens:.0f}:1\n")
        print(f"✓ Created: {token_file}")
        
        print(f"\n{'='*60}")
        print(f"AI-OPTIMIZED ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"Output Directory: {output_dir}")
        # Calculate realistic cost estimates
        cost_nano = (total_tokens * 0.05 / 1_000_000) + (total_tokens * 0.6 * 0.40 / 1_000_000)
        cost_mini = (total_tokens * 0.25 / 1_000_000) + (total_tokens * 0.6 * 2.00 / 1_000_000)
        cost_chat = (total_tokens * 1.25 / 1_000_000) + (total_tokens * 0.6 * 10.00 / 1_000_000)
        
        print(f"\nFiles created:")
        print(f"  1. summary.json - High-level overview (use for quick context)")
        print(f"  2. errors_detailed.json - All errors with packet numbers")
        print(f"  3. conversations.json - Top network conversations")
        print(f"  4. ai_analysis_prompt.md - Ready for AI analysis")
        print(f"  5. quick_stats.txt - Human-readable summary")
        print(f"  6. token_estimate.txt - Cost analysis")
        print(f"Estimated tokens: ~{total_tokens:,}")
        print(f"Estimated cost (Global deployment):")
        print(f"  gpt-5-chat: ${cost_chat:.4f} (recommended)")
        print(f"\n🚀 NEXT STEP: Run 'python analyze_with_ai.py --dir {output_dir}' for AI analysis")
        
    def _estimate_tokens(self, text):
        """Rough token estimation (1 token ≈ 4 characters)"""
        return len(text) // 4


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Prepare PCAP files for AI analysis by extracting errors and patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python prepare_for_ai_analysis.py --input sanitized.cap --output-dir analysis/
  
  # Use default output directory
  python prepare_for_ai_analysis.py --input sanitized.cap
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input PCAP file path'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default='ai_analysis',
        help='Output directory for analysis files (default: ai_analysis/)'
    )
    
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)
    
    pcap_file = args.input
    output_dir = args.output_dir
    
    try:
        # Validate input file
        if not pcap_file:
            print("❌ Error: No input file specified", file=sys.stderr)
            sys.exit(1)
            
        if not os.path.exists(pcap_file):
            print(f"❌ Error: PCAP file not found: {pcap_file}", file=sys.stderr)
            sys.exit(1)
            
        if not os.access(pcap_file, os.R_OK):
            print(f"❌ Error: Cannot read PCAP file (permission denied): {pcap_file}", file=sys.stderr)
            sys.exit(1)
            
        # Check file size
        file_size = os.path.getsize(pcap_file)
        if file_size == 0:
            print(f"❌ Error: Input file is empty (0 bytes): {pcap_file}", file=sys.stderr)
            sys.exit(1)
        
        # Validate output directory path
        if not output_dir:
            print("❌ Error: No output directory specified", file=sys.stderr)
            sys.exit(1)
            
        # Check if output directory parent exists and is writable
        parent_dir = os.path.dirname(os.path.abspath(output_dir)) if os.path.dirname(output_dir) else '.'
        if not os.path.exists(parent_dir):
            print(f"❌ Error: Parent directory does not exist: {parent_dir}", file=sys.stderr)
            sys.exit(1)
            
        if not os.access(parent_dir, os.W_OK):
            print(f"❌ Error: Cannot write to parent directory (permission denied): {parent_dir}", file=sys.stderr)
            sys.exit(1)
        
        # Display header
        print("="*60)
        print("PCAP TO AI-OPTIMIZED ANALYSIS")
        print("="*60)
        print(f"Input: {pcap_file}")
        print(f"Size: {file_size / (1024*1024):.2f} MB")
        print(f"Output: {output_dir}/")
        print()
        
        # Initialize analyzer
        try:
            analyzer = PCAPAnalysisPrep(pcap_file)
        except Exception as e:
            print(f"❌ Error: Failed to initialize analyzer: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Load and analyze packets
        try:
            print("Loading packets...")
            analyzer.load_packets()
            
            if analyzer.stats['total_packets'] == 0:
                print(f"❌ Error: No valid packets found in PCAP file: {pcap_file}", file=sys.stderr)
                sys.exit(1)
                
            print("Analyzing packets...")
            analyzer.analyze_all()
            
        except MemoryError:
            print(f"❌ Error: Out of memory while processing PCAP file (file too large)", file=sys.stderr)
            print(f"   Try splitting the file into smaller chunks using 'editcap'", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: Failed to analyze PCAP: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
        # Export analysis
        try:
            print("Exporting analysis...")
            analyzer.export_analysis(output_dir)
            print("\n✅ Analysis complete!")
            sys.exit(0)
            
        except PermissionError as e:
            print(f"❌ Error: Cannot write to output directory (permission denied): {output_dir}", file=sys.stderr)
            sys.exit(1)
        except OSError as e:
            if "No space left" in str(e) or "Disk quota exceeded" in str(e):
                print(f"❌ Error: No disk space available: {e}", file=sys.stderr)
            else:
                print(f"❌ Error: Failed to write output files: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: Failed to export analysis: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user", file=sys.stderr)
        # Clean up partial output directory if it was created
        if os.path.exists(output_dir) and os.path.isdir(output_dir):
            try:
                import shutil
                shutil.rmtree(output_dir)
                print(f"Cleaned up partial output directory: {output_dir}", file=sys.stderr)
            except:
                pass
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)
