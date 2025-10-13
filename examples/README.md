# Example Analysis Output

This directory contains sample outputs from analyzing a 423 MB AKS network capture.

## Files

- `summary.json` - High-level statistics and metrics
- `errors_detailed.json` - Specific error instances
- `conversations.json` - Top network flows
- `quick_stats.txt` - Human-readable summary
- `ai_analysis_errors.md` - AI-generated root cause analysis

## Sample Stats

```
Total Packets: 184,392
File Size: 423.15 MB

ERRORS FOUND:
  TCP Resets: 1,124
  Retransmissions: 58,437
  DNS Failures: 287
  HTTP Errors: 12
  Connection Failures: 743
```

## Key Findings

The AI analysis identified:

1. **Significant TCP retransmissions** (58K+) indicating packet loss
2. **CoreDNS misconfiguration** causing DNS resolution failures
3. **Azure CNI SNAT exhaustion** causing connection drops

## Root Cause

Network congestion and misconfigured DNS forwarding in AKS cluster, causing:
- Severe packet loss between nodes
- Failed DNS resolution for Azure endpoints
- Connection timeouts to Kubernetes API

## Resolution

Priority actions:
1. Fix CoreDNS ConfigMap to forward external domains
2. Increase SNAT port allocation for Azure CNI
3. Verify MTU settings across cluster nodes

## Cost

- Analysis tokens: 4,924
- Analysis cost: $0.0015 (gpt-5-chat)
- Compression: 423 MB → 4.9 KB (86,000:1)
