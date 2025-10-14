#!/usr/bin/env python3
"""
AI-Powered PCAP Analysis using GPT-5-chat (Azure OpenAI)

This script analyzes the prepared PCAP analysis data using Azure OpenAI's GPT-5-chat model
to provide intelligent insights into network issues, errors, and troubleshooting steps.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment from .env file in current directory or parent
load_dotenv()

class PCAPAIAnalyzer:
    """AI-powered PCAP analysis using Azure OpenAI"""
    
    def __init__(self, analysis_dir: str, model_override: str = None):
        """Initialize the analyzer with comprehensive error handling"""
        
        # Validate analysis directory
        if not analysis_dir:
            raise ValueError("Analysis directory path cannot be empty")
        
        self.analysis_dir = Path(analysis_dir)
        
        if not self.analysis_dir.exists():
            raise FileNotFoundError(f"Analysis directory not found: {analysis_dir}")
        
        if not self.analysis_dir.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {analysis_dir}")
        
        if not os.access(self.analysis_dir, os.R_OK):
            raise PermissionError(f"Cannot read analysis directory (permission denied): {analysis_dir}")
        
        # Check for required analysis files
        required_files = ['summary.json', 'errors_detailed.json']
        missing_files = []
        for filename in required_files:
            filepath = self.analysis_dir / filename
            if not filepath.exists():
                missing_files.append(filename)
        
        if missing_files:
            raise FileNotFoundError(
                f"Missing required analysis files in {analysis_dir}: {', '.join(missing_files)}\n"
                f"Run 'prepare_for_ai_analysis.py' first to generate these files."
            )
        
        # Initialize Azure OpenAI client
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        
        # Validate credentials
        if not self.endpoint:
            raise ValueError(
                "Azure OpenAI endpoint not found.\n"
                "Set AZURE_OPENAI_ENDPOINT environment variable or add to .env file"
            )
        
        if not self.api_key:
            raise ValueError(
                "Azure OpenAI API key not found.\n"
                "Set AZURE_OPENAI_API_KEY environment variable or add to .env file"
            )
        
        # Validate endpoint format
        if not self.endpoint.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid endpoint URL format: {self.endpoint}")
        
        # Allow model override or use GPT_5_CHAT_MODEL by default (better for analysis)
        if model_override:
            self.model = model_override
        else:
            self.model = os.getenv("GPT_5_CHAT_MODEL", "gpt-5-chat")
        
        # Initialize OpenAI client
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=f"{self.endpoint}/openai/v1/"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Azure OpenAI client: {e}")
        
        print(f"✅ Initialized Azure OpenAI client")
        print(f"   Endpoint: {self.endpoint}")
        print(f"   Model: {self.model}")
    
    def load_analysis_files(self):
        """Load all analysis files"""
        files = {
            'summary': self.analysis_dir / 'summary.json',
            'errors': self.analysis_dir / 'errors_detailed.json',
            'conversations': self.analysis_dir / 'conversations.json',
            'stats': self.analysis_dir / 'quick_stats.txt'
        }
        
        data = {}
        
        for key, filepath in files.items():
            if not filepath.exists():
                print(f"⚠️  Warning: {filepath} not found")
                continue
            
            if filepath.suffix == '.json':
                with open(filepath, 'r') as f:
                    data[key] = json.load(f)
            else:
                with open(filepath, 'r') as f:
                    data[key] = f.read()
        
        return data
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation"""
        return len(text) // 4
    
    def create_analysis_prompt(self, data: dict, focus: str = "general") -> str:
        """Create a focused analysis prompt"""
        
        summary = data.get('summary', {})
        errors = data.get('errors', {})
        conversations = data.get('conversations', [])
        
        # Build context-aware prompt based on focus
        if focus == "errors":
            prompt = f"""# Network Packet Capture Analysis - Error Focus

## Capture Overview
- **Total Packets**: {summary.get('metadata', {}).get('total_packets', 'N/A'):,}
- **File Size**: {summary.get('metadata', {}).get('file_size_mb', 'N/A'):.2f} MB
- **Source**: {summary.get('metadata', {}).get('source_file', 'N/A')}

## Error Summary
{json.dumps(summary.get('error_summary', {}), indent=2)}

## Top Sources
{json.dumps(summary.get('top_sources', [])[:5], indent=2)}

## Top Destinations
{json.dumps(summary.get('top_destinations', [])[:5], indent=2)}

## Top Destination Ports
{json.dumps(summary.get('top_ports', {}).get('destination', [])[:10], indent=2)}

## Critical Errors

### TCP Resets (Sample)
{json.dumps(errors.get('tcp_resets', [])[:10], indent=2)}

### TCP Retransmissions (Sample)
{json.dumps(errors.get('tcp_retransmissions', [])[:10], indent=2)}

### DNS Failures (Sample)
{json.dumps(errors.get('dns_failures', [])[:10], indent=2)}

### HTTP Errors (Sample)
{json.dumps(errors.get('http_errors', [])[:5], indent=2)}

## Analysis Request

This is from an **Azure AKS production escalation**. Based on the network capture data above, provide:

1. **Root Cause Analysis**: What is the primary issue causing these errors?
2. **Error Pattern Analysis**: What patterns do you see in the TCP resets, retransmissions, and failures?
3. **Service Impact**: Which services or endpoints are most affected?
4. **Network Path Issues**: Do the errors suggest client-side, network infrastructure, or server-side problems?
5. **Azure/AKS Specific Insights**: Any Azure-specific or Kubernetes networking issues?
6. **Prioritized Action Plan**: What should be done first to resolve these issues?

Provide specific evidence from the packet data and actionable recommendations."""

        elif focus == "performance":
            prompt = f"""# Network Performance Analysis

## Capture Overview
- **Total Packets**: {summary.get('metadata', {}).get('total_packets', 'N/A'):,}
- **Protocol Distribution**: {json.dumps(summary.get('protocol_distribution', {}), indent=2)}

## Performance Indicators

### Retransmissions
{json.dumps(errors.get('tcp_retransmissions', [])[:20], indent=2)}

### Top Conversations
{json.dumps(conversations[:10], indent=2)}

### TCP Flags Distribution
{json.dumps(summary.get('tcp_flags_distribution', {}), indent=2)}

## Analysis Request

Analyze the network performance:

1. **Retransmission Rate**: Is the retransmission rate acceptable or concerning?
2. **Latency Indicators**: What do the patterns suggest about latency?
3. **Bandwidth Utilization**: Are there signs of bandwidth saturation?
4. **Connection Quality**: What's the quality of TCP connections?
5. **Recommendations**: How can performance be improved?"""

        elif focus == "dns":
            prompt = f"""# DNS Resolution Analysis

## DNS Statistics
- **Total DNS Queries**: {len(summary.get('top_dns_queries', []))}
- **DNS Failures**: {len(errors.get('dns_failures', []))}

## Top DNS Queries
{json.dumps(summary.get('top_dns_queries', [])[:20], indent=2)}

## DNS Failures
{json.dumps(errors.get('dns_failures', [])[:30], indent=2)}

## Analysis Request

Analyze DNS issues:

1. **DNS Health**: Is DNS resolution working properly?
2. **Failure Patterns**: What patterns exist in DNS failures?
3. **Impact Analysis**: How do DNS issues affect the application?
4. **Resolution**: What needs to be fixed?"""

        else:  # general
            prompt = f"""# Comprehensive Network Packet Capture Analysis

## Executive Summary
{json.dumps(summary, indent=2)}

## Detailed Errors
{json.dumps(errors, indent=2)}

## Top Conversations
{json.dumps(conversations[:10], indent=2)}

## Analysis Request

This is from an **Azure AKS production escalation**. Provide a comprehensive analysis covering:

1. **Executive Summary**: High-level assessment of the network health
2. **Root Cause**: Primary issue causing problems
3. **Error Analysis**: Breakdown of all error types and their significance
4. **Pattern Recognition**: Any patterns in failures, timing, or endpoints
5. **Azure/AKS Considerations**: Kubernetes-specific or Azure networking issues
6. **Impact Assessment**: How severe are these issues?
7. **Actionable Recommendations**: Step-by-step troubleshooting plan with priorities

Be specific and reference actual data from the capture."""
        
        return prompt
    
    def analyze(self, focus: str = "general", save_output: bool = True) -> dict:
        """Run AI analysis on the PCAP data"""
        
        print(f"\n{'='*80}")
        print(f"AI-POWERED PCAP ANALYSIS - {focus.upper()} FOCUS")
        print(f"{'='*80}\n")
        
        # Load data
        print("📂 Loading analysis data...")
        data = self.load_analysis_files()
        
        if not data:
            print("❌ No analysis data found. Run prepare_for_ai_analysis.py first.")
            return {}
        
        print(f"✅ Loaded {len(data)} data files")
        
        # Create prompt
        print(f"🔍 Creating {focus} analysis prompt...")
        prompt = self.create_analysis_prompt(data, focus)
        
        # Estimate tokens
        estimated_tokens = self.estimate_tokens(prompt)
        estimated_cost = (estimated_tokens / 1_000_000) * 0.150 + (2000 / 1_000_000) * 0.600
        
        print(f"📊 Token estimate: ~{estimated_tokens:,}")
        print(f"💰 Estimated cost: ${estimated_cost:.4f}")
        print(f"\n🤖 Calling Azure OpenAI ({self.model})...")
        print("   This may take 30-60 seconds for reasoning models...\n")
        
        try:
            # Call Azure OpenAI
            # Use appropriate parameters based on model type
            kwargs = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert network and Azure/Kubernetes troubleshooting engineer. Analyze network packet captures to identify root causes, patterns, and provide actionable recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Reasoning models (gpt-5, gpt-5-mini, gpt-5-pro) require max_completion_tokens
            if 'gpt-5-mini' in self.model or 'gpt-5-pro' in self.model or self.model == 'gpt-5':
                kwargs["max_completion_tokens"] = 3000
            else:
                # Chat models use max_tokens and support temperature
                kwargs["max_tokens"] = 3000
                kwargs["temperature"] = 0.7
            
            response = self.client.chat.completions.create(**kwargs)
            
            # Extract response
            content = response.choices[0].message.content
            
            # Handle reasoning models that might not return visible content
            if not content:
                if (response.usage and 
                    hasattr(response.usage, 'completion_tokens_details') and
                    response.usage.completion_tokens_details and
                    hasattr(response.usage.completion_tokens_details, 'reasoning_tokens')):
                    reasoning_tokens = response.usage.completion_tokens_details.reasoning_tokens
                    content = f"⚠️ Model used {reasoning_tokens} reasoning tokens but returned no visible content. This may indicate the analysis was too complex. Try with a more specific focus."
            
            # Get usage stats
            usage = {
                'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                'total_tokens': response.usage.total_tokens if response.usage else 0,
                'reasoning_tokens': 0
            }
            
            if (response.usage and 
                hasattr(response.usage, 'completion_tokens_details') and
                response.usage.completion_tokens_details and
                hasattr(response.usage.completion_tokens_details, 'reasoning_tokens')):
                usage['reasoning_tokens'] = response.usage.completion_tokens_details.reasoning_tokens
            
            actual_cost = (usage['prompt_tokens'] / 1_000_000) * 0.150 + (usage['completion_tokens'] / 1_000_000) * 0.600
            
            result = {
                'focus': focus,
                'analysis': content,
                'usage': usage,
                'cost': actual_cost,
                'timestamp': datetime.now().isoformat(),
                'model': self.model
            }
            
            # Display results
            print(f"{'='*80}")
            print(f"ANALYSIS RESULTS")
            print(f"{'='*80}\n")
            print(content)
            print(f"\n{'='*80}")
            print(f"USAGE STATISTICS")
            print(f"{'='*80}")
            print(f"Prompt tokens: {usage['prompt_tokens']:,}")
            print(f"Completion tokens: {usage['completion_tokens']:,}")
            if usage['reasoning_tokens'] > 0:
                print(f"Reasoning tokens: {usage['reasoning_tokens']:,}")
            print(f"Total tokens: {usage['total_tokens']:,}")
            print(f"Actual cost: ${actual_cost:.4f}")
            print(f"{'='*80}\n")
            
            # Save output
            if save_output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.analysis_dir / f"ai_analysis_{focus}_{timestamp}.md"
                
                with open(output_file, 'w') as f:
                    f.write(f"# AI-Powered PCAP Analysis - {focus.upper()} Focus\n\n")
                    f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"**Model**: {self.model}\n")
                    f.write(f"**Tokens Used**: {usage['total_tokens']:,}\n")
                    f.write(f"**Cost**: ${actual_cost:.4f}\n\n")
                    f.write("---\n\n")
                    f.write(content)
                    f.write("\n\n---\n\n")
                    f.write("## Usage Statistics\n\n")
                    f.write(f"```json\n{json.dumps(usage, indent=2)}\n```\n")
                
                print(f"💾 Analysis saved to: {output_file}")
                
                # Also save JSON
                json_file = self.analysis_dir / f"ai_analysis_{focus}_{timestamp}.json"
                with open(json_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"💾 JSON saved to: {json_file}\n")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def compare_analyses(self, analysis_files: list):
        """Compare multiple AI analyses to find trends"""
        print(f"\n{'='*80}")
        print(f"COMPARING {len(analysis_files)} ANALYSES")
        print(f"{'='*80}\n")
        
        analyses = []
        for file in analysis_files:
            with open(file, 'r') as f:
                analyses.append(json.load(f))
        
        # Create comparison prompt
        prompt = f"""Compare these {len(analyses)} network analyses and identify:

1. **Common Themes**: What issues appear across all analyses?
2. **Evolution**: How have the issues changed over time?
3. **Priority Issues**: What should be addressed first?
4. **Success Metrics**: How will we know if fixes are working?

Analyses:
{json.dumps(analyses, indent=2)}"""
        
        print("🤖 Generating comparison analysis...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a network analysis expert comparing multiple analyses to find trends and priorities."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=2000
            )
            
            content = response.choices[0].message.content
            print(content)
            return content
            
        except Exception as e:
            print(f"❌ Error during comparison: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered PCAP Analysis using Azure OpenAI GPT-5-chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # General comprehensive analysis
  python analyze_with_ai.py
  
  # Focus on errors
  python analyze_with_ai.py --focus errors
  
  # Focus on performance
  python analyze_with_ai.py --focus performance
  
  # Focus on DNS issues
  python analyze_with_ai.py --focus dns
  
  # Custom analysis directory
  python analyze_with_ai.py --dir /path/to/ai_analysis
  
  # Compare multiple analyses
  python analyze_with_ai.py --compare ai_analysis/ai_analysis_*.json
        """
    )
    
    parser.add_argument(
        '--dir', '-d',
        default='ai_analysis',
        help='Path to analysis directory (default: ai_analysis/)'
    )
    
    parser.add_argument(
        '--focus',
        choices=['general', 'errors', 'performance', 'dns'],
        default='general',
        help='Analysis focus area (default: general)'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save analysis output to files'
    )
    
    parser.add_argument(
        '--compare',
        nargs='+',
        help='Compare multiple analysis JSON files'
    )
    
    parser.add_argument(
        '--model',
        choices=['gpt-5', 'gpt-5-chat', 'gpt-5-mini', 'gpt-5-pro'],
        help='Override model selection (default: gpt-5-chat for best analysis)'
    )
    
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(1)
    
    try:
        # Validate inputs
        if not args.dir:
            print("❌ Error: Analysis directory not specified", file=sys.stderr)
            sys.exit(1)
        
        # Initialize analyzer with error handling
        try:
            print("="*60)
            print("AI-POWERED PCAP ANALYSIS")
            print("="*60)
            print(f"Analysis Directory: {args.dir}")
            print(f"Focus: {args.focus}")
            print(f"Model: {args.model or 'gpt-5-chat (default)'}")
            print()
            
            analyzer = PCAPAIAnalyzer(args.dir, model_override=args.model)
            
        except FileNotFoundError as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except NotADirectoryError as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except PermissionError as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            print("\nTip: Check your .env file or environment variables:", file=sys.stderr)
            print("  - AZURE_OPENAI_ENDPOINT", file=sys.stderr)
            print("  - AZURE_OPENAI_API_KEY", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Perform analysis or comparison
        try:
            if args.compare:
                # Validate comparison files
                if not args.compare:
                    print("❌ Error: No comparison files specified", file=sys.stderr)
                    sys.exit(1)
                
                missing_files = [f for f in args.compare if not os.path.exists(f)]
                if missing_files:
                    print(f"❌ Error: Comparison files not found:", file=sys.stderr)
                    for f in missing_files:
                        print(f"  - {f}", file=sys.stderr)
                    sys.exit(1)
                
                analyzer.compare_analyses(args.compare)
            else:
                analyzer.analyze(
                    focus=args.focus,
                    save_output=not args.no_save
                )
            
            print("\n✅ Analysis complete!")
            sys.exit(0)
            
        except ConnectionError as e:
            print(f"\n❌ Error: Cannot connect to Azure OpenAI: {e}", file=sys.stderr)
            print("  Check your network connection and endpoint URL", file=sys.stderr)
            sys.exit(1)
        except TimeoutError as e:
            print(f"\n❌ Error: Request timed out: {e}", file=sys.stderr)
            print("  The API may be overloaded or your network is slow", file=sys.stderr)
            sys.exit(1)
        except MemoryError:
            print(f"\n❌ Error: Out of memory", file=sys.stderr)
            print("  Try using a smaller focus area or reducing the data size", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
                print(f"\n❌ Error: Authentication failed: {e}", file=sys.stderr)
                print("  Check your AZURE_OPENAI_API_KEY", file=sys.stderr)
                sys.exit(1)
            elif "rate limit" in error_msg or "429" in error_msg:
                print(f"\n❌ Error: Rate limit exceeded: {e}", file=sys.stderr)
                print("  Wait a moment and try again", file=sys.stderr)
                sys.exit(1)
            elif "quota" in error_msg:
                print(f"\n❌ Error: Quota exceeded: {e}", file=sys.stderr)
                print("  Check your Azure OpenAI quota and billing", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"\n❌ Error during analysis: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc()
                sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
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
