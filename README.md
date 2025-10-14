# 🔍 PCAP AI Analyzer

AI-powered network packet capture analyzer for troubleshooting network issues. Sanitizes sensitive data, detects errors, and uses Azure OpenAI to provide root cause analysis and actionable recommendations.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)]

## 🎯 Features

- **🔒 PII Sanitization**: Anonymizes IP addresses, MAC addresses, DNS queries, HTTP headers, emails, and API keys
- **📊 Error Detection**: Identifies TCP resets, retransmissions, DNS failures, HTTP errors, and connection issues
- **🤖 AI Analysis**: Uses Azure OpenAI GPT-5 models for root cause analysis
- **💰 Cost-Efficient**: Reduces 500MB PCAP files to ~5KB of structured data
- **🎯 Kubernetes Support**: Works well with AKS/K8s networking captures
- **📈 Actionable Insights**: Generates troubleshooting recommendations with evidence

## ⚠️ Security & Privacy Disclaimer

**This tool provides best-effort sanitization for common protocols. Always review output before external sharing.**

### ✅ What Sanitization DOES:
- Anonymizes IP/MAC addresses to reserved ranges (RFC 5737, RFC 1918)
- Removes HTTP headers (cookies, authorization, API keys)
- Sanitizes DNS queries and common PII patterns
- Preserves network behavior for troubleshooting

### ⚠️ What Sanitization DOES NOT Do:
- **Cannot decrypt TLS/SSL encrypted traffic** (encrypted payloads remain encrypted)
- **Only handles common protocols** (HTTP, DNS, TCP/IP - custom protocols may leak data)
- **Not 100% guaranteed** (obfuscated or custom data formats may not be detected)
- **Not a compliance-only solution** (GDPR/HIPAA/PCI-DSS require additional validation)

### 🔒 Best Practices:
1. **Always manually review** sanitized files before sharing externally
2. **Test on a sample** before processing large datasets
3. **Use full packet capture** (no snaplen truncation) for sensitive data
4. **Combine with organizational security policies** (access controls, encryption at rest)
5. **Document your review process** for audit trails

📋 **Detailed Testing:** See [SANITIZATION_TEST_REPORT.md](./docs/SANITIZATION_TEST_REPORT.md) for accuracy validation results.

**Recommended Use:** Internal troubleshooting, team collaboration, support cases (with review)  
**Requires Extra Review:** External vendor sharing, compliance-regulated data, public release

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Azure OpenAI API access
- `tshark`/Wireshark (optional, for advanced analysis)

**Note:** On Debian/Ubuntu systems, you may need:
```bash
sudo apt install python3-venv  # For virtual environment support
```

### Installation

```bash
# Clone the repository
git clone https://github.com/rkemery-msft/pcap-ai-analyzer.git
cd pcap-ai-analyzer

# Install dependencies
pip install -r requirements.txt

# Configure Azure OpenAI credentials
cp .env.example .env
# Edit .env with your Azure OpenAI endpoint and API key
```

### Basic Usage

```bash
# 1. Sanitize a PCAP file (remove PII)
python sanitize_pcap.py --input capture.cap --output sanitized.cap

# 2. Prepare for AI analysis
python prepare_for_ai_analysis.py --input sanitized.cap --output-dir analysis/

# 3. Run AI analysis
python analyze_with_ai.py --dir analysis/ --focus errors
```

## 📖 Detailed Usage

### Step 1: Sanitize PCAP Files

Remove sensitive customer data while preserving network patterns:

```bash
python sanitize_pcap.py \
  --input /path/to/capture.cap \
  --output /path/to/sanitized.cap \
  --preserve-private-ips
```

**What gets sanitized:**
- ✅ IP addresses (consistent anonymization)
- ✅ MAC addresses
- ✅ DNS queries/responses
- ✅ HTTP headers (Authorization, Cookie, User-Agent, etc.)
- ✅ Email addresses
- ✅ API keys and tokens

**What's preserved:**
- ✅ Packet timing and structure
- ✅ Protocol hierarchy
- ✅ Traffic patterns
- ✅ Error indicators

### Step 2: Extract and Organize Data

Transform packet data into AI-ready format:

```bash
python prepare_for_ai_analysis.py \
  --input sanitized.cap \
  --output-dir ai_analysis/
```

**Output files:**
- `summary.json` - High-level statistics and error counts
- `errors_detailed.json` - Specific error instances with packet numbers
- `conversations.json` - Top network flows and conversations
- `ai_analysis_prompt.md` - Ready-to-use prompt for manual AI analysis
- `quick_stats.txt` - Human-readable summary
- `token_estimate.txt` - Cost estimation

**Compression:** 500MB → ~5KB of structured insights (100,000:1 ratio)

### Step 3: AI-Powered Analysis

Generate intelligent troubleshooting recommendations:

```bash
# General comprehensive analysis (gpt-5-chat recommended)
python analyze_with_ai.py --dir ai_analysis/

# Focus on specific areas
python analyze_with_ai.py --dir ai_analysis/ --focus errors
python analyze_with_ai.py --dir ai_analysis/ --focus performance
python analyze_with_ai.py --dir ai_analysis/ --focus dns

# Use gpt-5-chat model (recommended for consistent output)
python analyze_with_ai.py --dir ai_analysis/ --model gpt-5-chat

# Use gpt-5 for balanced reasoning (moderate processing time)
python analyze_with_ai.py --dir ai_analysis/ --focus errors --model gpt-5

# Use gpt-5-mini for detailed reasoning (longer processing time)
python analyze_with_ai.py --dir ai_analysis/ --focus errors --model gpt-5-mini
```

**Analysis Focus Areas:**
- `general` - Comprehensive overview (default, use with gpt-5-chat)
- `errors` - Deep dive into failures and issues
- `performance` - Network performance and optimization
- `dns` - DNS-specific troubleshooting

**Model Selection:**
- **gpt-5-chat**: Fast, consistent, recommended for all scenarios
- **gpt-5**: Balanced reasoning model, good compromise between speed and depth
- **gpt-5-mini**: Detailed reasoning, best with specific focus areas (errors, performance, dns)

## 🔧 Configuration

### Environment Variables

Create a `.env` file with your Azure OpenAI credentials:

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-01

# Model Deployment Names
# Use your actual Azure OpenAI deployment names
GPT_5_CHAT_MODEL=gpt-5-chat    # Recommended: Fast, consistent output
GPT_5_MODEL=gpt-5              # Optional: Balanced reasoning model
GPT_5_MINI_MODEL=gpt-5-mini    # Optional: Detailed reasoning (slower)
```

**Model Information:**
- **gpt-5-chat** (128K context): Standard chat model optimized for fast, consistent analysis. **Recommended for most users.**
- **gpt-5** (128K context): Balanced reasoning model with moderate processing time. Good compromise between speed and analytical depth.
- **gpt-5-mini** (400K context): Reasoning model with extended thinking capabilities. Use for complex technical deep-dives with specific focus areas.

### Advanced Options

#### Sanitization Options

```python
# In sanitize_pcap.py, customize the sanitizer:
sanitizer = PCAPSanitizer(
    preserve_internal_ips=True,  # Keep 10.x, 172.16.x, 192.168.x recognizable
    anonymize_domains=True,       # Hash domain names
    remove_payloads=False         # Keep HTTP/payload data
)
```

#### Analysis Customization

```python
# In analyze_with_ai.py, adjust parameters:
response = client.chat.completions.create(
    model=model,
    max_tokens=3000,        # Increase for detailed analysis
    temperature=0.7,        # Adjust creativity (0.0-1.0)
)
```

## 📊 Example Output

### Error Detection Results

```
PCAP ANALYSIS - QUICK STATS
============================================================

Total Packets: 184,392
File Size: 423.15 MB

ERRORS FOUND:
  TCP Resets: 1,124
  Retransmissions: 58,437
  DNS Failures: 287
  HTTP Errors: 12
  Connection Failures: 743

PROTOCOLS:
  IPv4: 184,201
  TCP: 182,956
  UDP: 1,245

TOP DESTINATIONS:
  10.142.78.201: 41,283 packets
  10.198.234.89: 39,567 packets
```

### AI Analysis Sample

```
Root Cause Analysis:
The dominant error type is TCP retransmissions (58,437 out of 60,603 total 
errors, >96%), indicating severe packet loss or delayed acknowledgments 
along the network path.

Primary Issue:
- Azure CNI SNAT port exhaustion causing dropped connections
- CoreDNS misconfiguration for external Azure domain resolution
- Node-to-node connectivity issues in AKS cluster

Priority Actions:
1. Fix CoreDNS forward rules for Azure endpoints
2. Validate Azure CNI SNAT availability
3. Check MTU settings and node NIC health
```

## 💰 Cost Analysis

### Azure OpenAI GPT-5 Pricing (Global Deployment)

| File Size | Tokens | gpt-5-chat Cost |
|-----------|--------|-----------------|
| 100 MB    | ~2,000 | **$0.0025** |
| 500 MB    | ~7,000 | **$0.0094** |
| 1 GB      | ~13,000| **$0.0175** |
| 5 GB      | ~35,000 | **$0.0938** |

**Model Information:**

- **gpt-5-chat** (Recommended): Standard chat model ($1.25 input / $10.00 output per 1M tokens)
  - 128K context window
  - Consistent, reliable output across all scenarios
  - Fast response time (typically 10-30 seconds)
  - Cost-effective at ~$0.001-$0.01 per typical capture
  - **Best for production use**

- **gpt-5** (Balanced): Reasoning model ($1.25 input / $10.00 output per 1M tokens)
  - 128K context window
  - Moderate reasoning capabilities with good output quality
  - Medium response time (30-60 seconds)
  - Similar pricing to gpt-5-chat but with reasoning tokens
  - **Good compromise between speed and analytical depth**

- **gpt-5-mini** (Alternative): Reasoning model ($0.50 input / $2.00 output per 1M tokens)
  - 400K context window (272K input / 128K output)
  - Uses extended reasoning for complex analysis
  - Longer response time (30-90 seconds)
  - Slightly higher cost due to reasoning tokens
  - Excellent for detailed technical deep-dives
  - **Use for specific focus areas** (errors, performance, dns)

**Important Notes:** 
- Costs shown are for AI analysis only using Global deployment (East US pricing)
- Sanitization and preparation are free (local processing)
- Data Zone deployments add ~10% to costs
- Cached input pricing (90% discount) available for repeated analyses
- See [GPT5_PRICING_REFERENCE.md](docs/GPT5_PRICING_REFERENCE.md) for detailed calculations
- Source: [Azure OpenAI Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)

## 🏗️ Architecture

```
┌─────────────────┐
│  Raw PCAP File  │
│   (500 MB)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Sanitize      │  ← Remove PII, anonymize IPs/MACs
│  (sanitize_pcap)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sanitized PCAP  │
│   (500 MB)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Extract &     │  ← Detect errors, analyze patterns
│   Organize      │
│ (prepare_for_ai)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Structured Data │  ← JSON summaries (~5 KB)
│   (5 KB)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Analysis    │  ← Azure OpenAI GPT-5 models
│ (analyze_with_ai)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Root Cause      │  ← Markdown report with actions
│   Report        │
└─────────────────┘
```

## 🔍 What Gets Detected

### Network Errors
- TCP resets (connection failures)
- TCP retransmissions (packet loss indicators)
- Connection failures (unanswered SYN packets)
- ICMP destination unreachable

### DNS Issues
- Failed queries (NXDOMAIN, SERVFAIL, etc.)
- Resolution timeouts
- Misconfigured forwarders

### HTTP/Application Errors
- 4xx client errors (400, 401, 403, 404)
- 5xx server errors (500, 502, 503, 504)
- Timeout indicators

### Performance Indicators
- High retransmission rates
- Large packet sizes (fragmentation)
- Connection duration and throughput
- TCP flag patterns

## 🎯 Use Cases

### DevOps / SRE
- **Incident Response**: Quickly identify root causes in production outages
- **Performance Tuning**: Detect network bottlenecks and optimization opportunities
- **Capacity Planning**: Analyze traffic patterns and growth trends

### Network Engineers
- **Troubleshooting**: Automated first-level analysis of connectivity issues
- **Documentation**: Generate detailed reports for escalations
- **Validation**: Verify network changes and configurations

### Security Teams
- **Forensics**: Analyze captured traffic while protecting sensitive data
- **Threat Hunting**: Identify anomalous connection patterns
- **Compliance**: Sanitize captures for sharing with third parties

### Cloud Architects (Azure/AKS)
- **AKS Networking**: Diagnose CNI, CoreDNS, and service mesh issues
- **Azure Connectivity**: Troubleshoot VNet, NSG, and load balancer problems
- **Monitoring**: Automated analysis of Network Watcher captures

## 🛠️ Troubleshooting

### Common Issues

**"No module named 'scapy'"**
```bash
pip install scapy
```

**"Azure OpenAI authentication failed"**
- Verify `.env` file exists and contains correct credentials
- Check endpoint URL format: `https://your-resource.openai.azure.com/`
- Ensure API key is active and has proper permissions

**"Out of memory processing large PCAP"**
- Process file in chunks using `editcap`:
  ```bash
  editcap -c 50000 large.cap split.cap
  ```
- Increase system memory or use a machine with more RAM

**"AI model returns no content" or "slow responses"**
- **Recommended:** Use `--model gpt-5-chat` for fast, consistent responses
- **gpt-5:** Balanced reasoning model (30-60 sec) with good analytical depth
  - Works well with all focus areas
  - Good compromise between speed and reasoning quality
- **gpt-5-mini:** Takes longer (30-90 sec) as it uses extended reasoning
  - Best with specific focus: `--focus errors`, `--focus performance`, or `--focus dns`
  - Avoid general focus with large datasets when using gpt-5-mini
  - If you see empty output, try gpt-5-chat or gpt-5 instead

### Virtual Environment Creation Fails

**Symptom:** `setup.sh` fails with "ensurepip is not available"

**Solution:**  
On Debian/Ubuntu:
```bash
sudo apt install python3-venv
```

Or install dependencies globally:
```bash
pip3 install -r requirements.txt
```

### Azure OpenAI Connection Errors

**Symptom:** "Azure OpenAI credentials not found"

**Solution:**  
Create `.env` file with your credentials:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
GPT_5_CHAT_MODEL=gpt-5-chat
```

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [Error Handling Reference](docs/ERROR_HANDLING.md)
- [Sanitization Test Report](docs/SANITIZATION_TEST_REPORT.md)
- [Pricing Reference](docs/GPT5_PRICING_REFERENCE.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/rkemery-msft/pcap-ai-analyzer.git
cd pcap-ai-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Scapy](https://scapy.net/) for packet manipulation
- Powered by [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- Inspired by real-world AKS troubleshooting scenarios

## 📞 Support

- 🐛 [Report Issues](https://github.com/rkemery-msft/pcap-ai-analyzer/issues)
- 💬 [Discussions](https://github.com/rkemery-msft/pcap-ai-analyzer/discussions)
- 📧 Email: rickkemery@microsoft.com

## 🗺️ Roadmap

- [ ] Support for more AI providers (OpenAI, Anthropic, local models)
- [ ] Real-time packet capture analysis
- [ ] Web UI for visualization
- [ ] Docker containerization
- [ ] Integration with Azure Monitor and Network Watcher
- [ ] Support for pcapng format
- [ ] Batch processing of multiple captures
- [ ] Custom rule engine for detection

## ⭐ Star History

If you find this tool useful, please consider giving it a star! ⭐

---

**Made with ❤️ for DevOps and Network Engineers**
