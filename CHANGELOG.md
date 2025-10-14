# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-14

### Fixed
- **Corrected gpt-5 context window in README.md**
  - Updated from incorrect 128K to correct 400K context window (272K input / 128K output)
  - Verified against Microsoft Azure OpenAI documentation
  - All GPT-5 reasoning models (gpt-5, gpt-5-mini) have 400K context, only gpt-5-chat has 128K
- **Corrected gpt-5-mini pricing in README.md**
  - Updated input pricing from $0.50 to $0.25 per 1M tokens (50% reduction)
  - Aligned with GPT5_PRICING_REFERENCE.md which had correct pricing
  - Validated through comprehensive Azure OpenAI testing
  - Users now have accurate cost information showing gpt-5-mini is 5x cheaper than gpt-5-chat
  - See `docs/PRICING_VALIDATION_REPORT.md` for full analysis
- **Improved accuracy of model capability descriptions**
  - Removed inaccurate "extended reasoning" claim for gpt-5-mini
  - Corrected: gpt-5 and gpt-5-mini have **identical reasoning capabilities**
  - Microsoft docs confirm: "absolute latency and cost scale down with mini and nano but the tradeoffs are the same"
  - Both support same reasoning_effort levels: minimal, low, medium, high
  - Main differences are cost (5x) and training data date, NOT reasoning depth
  - Added comprehensive pricing table showing all three models
  - Removed subjective "production" and "deep-dive excellence" claims
  - Added disclaimers that response times vary by reasoning_effort and workload

### Changed
- Reorganized repository structure for better navigation
  - Moved documentation to `docs/` directory
  - Moved tests to `tests/` directory
- Updated documentation to use clearer language
- Cleaned up redundant files
- Updated file path references in README and documentation
- **Removed gpt-5-pro support** - focused on three core models only (gpt-5-chat, gpt-5, gpt-5-mini)

### Added
- **gpt-5 model support** with optimized configuration
  - Increased `max_completion_tokens` to 16000 for comprehensive reasoning output
  - Balanced reasoning model between gpt-5-chat (fast) and gpt-5-mini (detailed)
  - Added documentation for gpt-5 usage and pricing
  - Works well with all focus areas

### Improved
- Enhanced reasoning model support (gpt-5, gpt-5-mini, gpt-5-pro)
  - Increased `max_completion_tokens` from 8000 to 16000 for gpt-5 models
  - Added `reasoning_effort: medium` parameter for better quality analysis
  - Significantly improved output consistency for complex prompts
  - All reasoning models now produce detailed analysis consistently
- Better error messages when reasoning models return empty content
  - Detects reasoning token usage and provides helpful guidance
  - Suggests alternative models and focus areas
  - Includes troubleshooting steps

### Removed
- Redundant testing report files

## [1.0.0] - 2025-10-13

### Added
- Initial release of PCAP AI Analyzer
- `sanitize_pcap.py` - PII sanitization for PCAP files
  - IP address anonymization with consistent mapping
  - MAC address anonymization
  - DNS query/response sanitization
  - HTTP header sanitization (cookies, auth, API keys)
  - Email address removal
  - Configurable private IP preservation
- `prepare_for_ai_analysis.py` - Error extraction and analysis preparation
  - TCP error detection (resets, retransmissions)
  - DNS failure detection
  - HTTP error detection
  - Connection failure analysis
  - Network conversation tracking
  - Token-optimized output generation
- `analyze_with_ai.py` - AI-powered root cause analysis
  - Azure OpenAI integration
  - Multiple analysis focus areas (general, errors, performance, DNS)
  - Support for Azure OpenAI GPT-5 models
  - Automated cost estimation
  - Markdown and JSON output formats
- Comprehensive documentation
  - README with features, usage, and examples
  - QUICKSTART guide for new users
  - CONTRIBUTING guidelines
  - LICENSE (MIT)
- Setup automation
  - `setup.sh` for quick installation
  - `.env.example` template for configuration
  - `.gitignore` for clean repository
- Example outputs and analysis samples

### Features
- 🔒 PII sanitization while preserving traffic patterns
- 📊 Error detection and classification
- 🤖 AI-powered root cause analysis with recommendations
- 💰 Cost-efficient analysis ($0.001-$0.031 per 500MB file)
- 🎯 Works well with Kubernetes/AKS captures
- 📈 Data compression (~100,000:1 ratio)
- 🔧 Command-line interface with options
- 📝 Documentation with examples and guides

### Technical Details
- Python 3.8+ compatibility
- Scapy-based packet processing
- Azure OpenAI SDK integration
- Deterministic anonymization (same input → same output)
- Memory-efficient streaming for large files
- Detailed usage statistics and cost tracking

---

## Future Roadmap

### [1.1.0] - Planned
- [ ] Support for OpenAI (non-Azure) API
- [ ] Real-time packet capture analysis
- [ ] Web UI for visualization
- [ ] Docker containerization
- [ ] Batch processing of multiple files

### [2.0.0] - Planned
- [ ] Support for additional AI providers (Anthropic Claude, local models)
- [ ] Custom detection rule engine
- [ ] Integration with Azure Network Watcher
- [ ] REST API for programmatic access
- [ ] Database backend for historical analysis

---

## Release Notes

### Version 1.0.0

This is the initial public release of PCAP AI Analyzer, a tool born from real-world Azure AKS troubleshooting scenarios. 

**Key Highlights:**
- Reduces 500MB PCAP files to actionable insights for ~$0.001-$0.01 (gpt-5-chat)
- Identifies root causes that would take hours of manual analysis
- Production-tested on Azure Kubernetes Service network captures
- Fully sanitized for sharing with vendors and support teams

**Use Cases:**
- DevOps incident response
- Network troubleshooting automation
- Security forensics (with PII protection)
- Azure/AKS escalation support

**Tested With:**
- Azure OpenAI GPT-5 series models
- PCAP files ranging from 100MB to 1GB
- Various network protocols (TCP, UDP, DNS, HTTP, TLS)
- AKS cluster captures with 200K+ packets

---

For detailed changes, see the [commit history](https://github.com/rkemery-msft/pcap-ai-analyzer/commits/main).
