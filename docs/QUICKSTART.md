# Quick Start Guide

Get started with PCAP AI Analyzer in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Azure OpenAI API access
- A PCAP file to analyze

**Note:** On Debian/Ubuntu systems, you may need to install `python3-venv`:
```bash
sudo apt install python3-venv
```

## Installation

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/rkemery-msft/pcap-ai-analyzer.git
cd pcap-ai-analyzer

# Run setup script
./setup.sh
```

### Option 2: Manual Setup

```bash
```bash
# Clone repository
git clone https://github.com/rkemery-msft/pcap-ai-analyzer.git
cd pcap-ai-analyzer

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your Azure OpenAI credentials
```

## Configuration

Edit `.env` file with your Azure OpenAI credentials:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-01

GPT_5_CHAT_MODEL=gpt-5-chat
```

### Getting Azure OpenAI Credentials

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint"
4. Copy:
   - Endpoint URL
   - One of the API keys
5. Note your model deployment names

## Usage

### Step 1: Sanitize Your PCAP File

Remove sensitive data while preserving network patterns:

```bash
python sanitize_pcap.py --input capture.cap --output sanitized.cap
```

**Output:**
```
PCAP SANITIZATION TOOL
============================================================
Input file: capture.cap
Input size: 423.15 MB
Output file: sanitized.cap

✓ Created: sanitized.cap
Total packets processed: 184,392
IP addresses anonymized: 368,784
MAC addresses anonymized: 368,912
DNS queries sanitized: 1,076
```

### Step 2: Prepare for AI Analysis

Extract errors and patterns into structured format:

```bash
python prepare_for_ai_analysis.py --input sanitized.cap --output-dir analysis/
```

**Output:**
```
PCAP TO AI-OPTIMIZED ANALYSIS
============================================================
Loaded 184,392 packets
Analyzing packets for errors and anomalies...
Analysis complete!

Files created:
  1. summary.json - High-level overview
  2. errors_detailed.json - All errors with packet numbers
  3. conversations.json - Top network conversations
  4. ai_analysis_prompt.md - Ready-to-paste prompt
  5. quick_stats.txt - Human-readable summary

Estimated tokens: ~3,070
Estimated cost: $0.001-$0.031 (varies by GPT-5 model)
```

### Step 3: Run AI Analysis

Get intelligent troubleshooting recommendations:

```bash
# General analysis
python analyze_with_ai.py --dir analysis/

# Focus on specific areas
python analyze_with_ai.py --dir analysis/ --focus errors
python analyze_with_ai.py --dir analysis/ --focus performance
python analyze_with_ai.py --dir analysis/ --focus dns

# Use specific model
# Use gpt-5-chat model (recommended)
python analyze_with_ai.py --dir analysis/ --model gpt-5-chat
```

**Output:**
```
AI-POWERED PCAP ANALYSIS - ERRORS FOCUS
============================================================

Root Cause Analysis:
The dominant error type is TCP retransmissions (71,171 out of 72,843 
total errors, >97%), indicating severe packet loss...

Prompt tokens: 3,138
Completion tokens: 1,786
Total tokens: 4,924
Actual cost: $0.0015 (gpt-5-chat Global deployment)
```

**Output:**
```
AI-POWERED PCAP ANALYSIS - ERRORS FOCUS
============================================================

Root Cause Analysis:
The dominant error type is TCP retransmissions (71,171 out of 72,843 
total errors, >97%), indicating severe packet loss...

Priority Actions:
1. Fix CoreDNS forward rules for Azure endpoints
2. Validate Azure CNI SNAT availability
3. Check MTU settings and node NIC health

Analysis saved to: analysis/ai_analysis_errors_20251013_141731.md
Actual cost: $0.006 (gpt-5-mini Global deployment)
```

## Example Workflow

Here's a complete example analyzing an AKS networking issue:

```bash
# 1. Sanitize the capture
python sanitize_pcap.py \
  --input aks-capture.cap \
  --output sanitized-aks.cap

# 2. Prepare for analysis
python prepare_for_ai_analysis.py \
  --input sanitized-aks.cap \
  --output-dir aks-analysis/

# 3. Run error-focused analysis
python analyze_with_ai.py \
  --dir aks-analysis/ \
  --focus errors \
  --model gpt-5-chat

# 4. View the results
cat aks-analysis/ai_analysis_errors_*.md
```

## Common Options

### Sanitization Options

```bash
# Keep private IPs recognizable (default)
python sanitize_pcap.py --input in.cap --output out.cap --preserve-private-ips

# Anonymize all IPs including private
python sanitize_pcap.py --input in.cap --output out.cap --no-preserve-private-ips

# Default output with auto-generated filename
python sanitize_pcap.py --input capture.cap
# Creates: sanitized_capture_<timestamp>.cap
```

**Analysis Focus Areas:**
- `general` - Comprehensive overview (default)
- `errors` - TCP resets, retransmissions, failures
- `performance` - Latency, throughput, optimization
- `dns` - DNS resolution issues

### Model Selection

**Model Selection:**
- `gpt-5-chat` (128K context) - Fast, no reasoning (best for speed)
- `gpt-5` (400K context) - Full reasoning model (same cost as chat, slower)
- `gpt-5-mini` (400K context) - Full reasoning model (5x cheaper, similar speed to gpt-5)

## Quick Reference

| Command | Purpose |
|---------|---------|
| `sanitize_pcap.py` | Remove PII from PCAP files |
| `prepare_for_ai_analysis.py` | Extract errors and create summaries |
| `analyze_with_ai.py` | Run AI-powered analysis |

## Troubleshooting

### "No module named 'scapy'"
```bash
pip install scapy
```

### "Virtual environment creation failed"
On Debian/Ubuntu, install python3-venv:
```bash
sudo apt install python3-venv
```
Or skip virtual environment and install globally:
```bash
pip3 install -r requirements.txt
```

### "Azure OpenAI authentication failed"
- Check your `.env` file exists
- Verify endpoint URL format (should end with `.openai.azure.com/`)
- Ensure API key is correct and active
- Verify API version matches your deployment

### "Out of memory"
Split large files:
```bash
editcap -c 50000 large.cap split.cap
```

### "Model returns no content"
Use a chat model instead:
```bash
python analyze_with_ai.py --model gpt-5-chat
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [examples/](examples/) for sample analyses
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Getting Help

- 🐛 [Report Issues](https://github.com/rkemery-msft/pcap-ai-analyzer/issues)
- 💬 [Discussions](https://github.com/rkemery-msft/pcap-ai-analyzer/discussions)
- 📖 [Full Documentation](README.md)

## Cost Estimate

### Azure OpenAI GPT-5-chat Pricing (Global Deployment)

| File Size | gpt-5-chat (Recommended) | Processing Time |
|-----------|-------------------------|------------------|
| 100 MB    | **$0.0025**             | 20-30 min       |
| 500 MB    | **$0.0094**             | 60-90 min       |
| 1 GB      | **$0.0175**             | 90-120 min      |
| 5 GB      | **$0.0938**             | 180-240 min     |

**💡 Recommendation:** Use `gpt-5-chat` ($1.25 input / $10.00 output per 1M tokens) for excellent quality and reliable output.

**Pricing Details:**
- **gpt-5-chat**: $1.25 input / $10.00 output per 1M tokens
- **128K context window**
- Typical analysis costs $0.001-$0.01 per capture

**Note:** Prices shown are for Global deployment in East US region (October 2025). Data Zone deployments add ~10%. See [GPT5_PRICING_REFERENCE.md](GPT5_PRICING_REFERENCE.md) for detailed calculations and [Azure OpenAI Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/) for current rates.

---

**You're ready to go! 🚀**

Start analyzing your network captures with AI-powered insights.
