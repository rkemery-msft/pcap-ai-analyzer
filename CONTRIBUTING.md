# Contributing to PCAP AI Analyzer

Thank you for your interest in contributing to PCAP AI Analyzer! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Sample PCAP file (sanitized) if possible

### Suggesting Features

Feature requests are welcome! Please create an issue with:
- Clear description of the feature
- Use case and benefits
- Proposed implementation (optional)

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/rkemery-msft/pcap-ai-analyzer.git
   cd pcap-ai-analyzer
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow PEP 8 style guidelines
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Test with sample PCAP
   python sanitize_pcap.py --input sample.cap --output test.cap
   python prepare_for_ai_analysis.py --input test.cap
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## 📝 Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Write docstrings for functions and classes
- Keep functions focused and under 50 lines when possible
- Use meaningful variable names

Example:
```python
def analyze_packet(packet: Packet, analyzer: PacketAnalyzer) -> AnalysisResult:
    """
    Analyze a single packet for errors and anomalies.
    
    Args:
        packet: The packet to analyze
        analyzer: The analyzer instance with configuration
        
    Returns:
        AnalysisResult containing findings and metrics
    """
    # Implementation
    pass
```

## 🧪 Testing

- Add tests for new features
- Ensure existing tests pass
- Test with various PCAP sizes and formats
- Test error handling and edge cases

## 📚 Documentation

- Update README.md if adding features
- Add docstrings to new functions
- Update examples if changing CLI
- Add comments for complex logic

## 🎯 Areas for Contribution

Contributions welcome in:
- Support for additional AI providers (OpenAI, Anthropic)
- Real-time packet capture analysis
- Web UI for visualization
- Docker containerization
- Additional error detection patterns
- Performance optimizations
- Test coverage improvements

## 🏗️ Development Setup

```bash
# Clone repository
git clone https://github.com/rkemery-msft/pcap-ai-analyzer.git
cd pcap-ai-analyzer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

## ❓ Questions

If you have questions:
- Check existing issues and discussions
- Create a new discussion for general questions
- Tag maintainers in PRs if you need review

## 📜 Code of Conduct

- Be respectful and constructive
- Welcome newcomers
- Focus on the code, not the person
- Assume good intentions

## 🎖️ Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🙌
