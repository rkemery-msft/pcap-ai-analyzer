# GPT-5 Pricing Reference (Azure OpenAI)

## ⚠️ NON-PRODUCTION TOOL DISCLAIMER

**This pricing reference is for experimental AI analysis tools.**

- ❌ NOT production-ready - For testing and development use
- ⚠️ AI Analysis requires explicit user consent for data submission

See main README.md for complete disclaimer.

---

**Source:** [Azure OpenAI Service Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/) (East US Region, as of October 2025)

**Recommended Model:** gpt-5-chat - Best balance of quality, reliability, and cost for PCAP analysis.

**Note:** Prices shown are current as of documentation date. Always refer to the [official Azure OpenAI pricing page](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/) for latest rates. Pricing may vary by region and agreement type.

## Azure OpenAI GPT-5 Series Pricing (Per 1M Tokens)

### gpt-5-chat (128K context, chat-optimized)
- **Global Deployment:**
  - Input: $1.25 / 1M tokens
  - Cached Input: $0.13 / 1M tokens
  - Output: $10.00 / 1M tokens

- **Data Zone Deployment (US/EU):**
  - Input: $1.38 / 1M tokens
  - Cached Input: $0.14 / 1M tokens
  - Output: $11.00 / 1M tokens

### gpt-5 (400K context, reasoning model)
- **Global Deployment:**
  - Input: $1.25 / 1M tokens
  - Cached Input: $0.13 / 1M tokens
  - Output: $10.00 / 1M tokens

- **Data Zone Deployment (US/EU):**
  - Input: $1.38 / 1M tokens
  - Cached Input: $0.14 / 1M tokens
  - Output: $11.00 / 1M tokens

### gpt-5-mini (400K context, reasoning model)
- **Global Deployment:**
  - Input: $0.25 / 1M tokens
  - Cached Input: $0.03 / 1M tokens
  - Output: $2.00 / 1M tokens

- **Data Zone Deployment (US/EU):**
  - Input: $0.28 / 1M tokens
  - Cached Input: $0.03 / 1M tokens
  - Output: $2.20 / 1M tokens

### gpt-5-nano (400K context, most cost-effective)
- **Global Deployment:**
  - Input: $0.05 / 1M tokens
  - Cached Input: $0.01 / 1M tokens
  - Output: $0.40 / 1M tokens

- **Data Zone Deployment (US/EU):**
  - Input: $0.06 / 1M tokens
  - Cached Input: $0.01 / 1M tokens
  - Output: $0.44 / 1M tokens

## PCAP Analysis Cost Scenarios (Global Deployment)

### Scenario 1: Small Network Capture (100 MB PCAP)
**Compression:** 100 MB → ~2,000 tokens (analysis input)  
**Expected Output:** ~1,500 tokens

| Model | Input Cost | Output Cost | Total Cost |
|-------|------------|-------------|------------|
| **gpt-5-chat** | $0.0025 | $0.0150 | **$0.0175** |
| **gpt-5-mini** | $0.0005 | $0.0030 | **$0.0035** |
| **gpt-5-nano** | $0.0001 | $0.0006 | **$0.0007** |

**Calculation Example (gpt-5-mini):**
- Input: 2,000 tokens × $0.25 / 1M = $0.0005
- Output: 1,500 tokens × $2.00 / 1M = $0.0030
- Total: **$0.0035**

### Scenario 2: Medium Network Capture (500 MB PCAP)
**Compression:** 500 MB → ~5,000 tokens (analysis input)  
**Expected Output:** ~2,500 tokens

| Model | Input Cost | Output Cost | Total Cost |
|-------|------------|-------------|------------|
| **gpt-5-chat** | $0.0063 | $0.0250 | **$0.0313** |
| **gpt-5-mini** | $0.0013 | $0.0050 | **$0.0063** |
| **gpt-5-nano** | $0.0003 | $0.0010 | **$0.0013** |

**Calculation Example (gpt-5-mini):**
- Input: 5,000 tokens × $0.25 / 1M = $0.0013
- Output: 2,500 tokens × $2.00 / 1M = $0.0050
- Total: **$0.0063**

### Scenario 3: Large Network Capture (1 GB PCAP)
**Compression:** 1 GB → ~8,000 tokens (analysis input)  
**Expected Output:** ~3,000 tokens

| Model | Input Cost | Output Cost | Total Cost |
|-------|------------|-------------|------------|
| **gpt-5-chat** | $0.0100 | $0.0300 | **$0.0400** |
| **gpt-5-mini** | $0.0020 | $0.0060 | **$0.0080** |
| **gpt-5-nano** | $0.0004 | $0.0012 | **$0.0016** |

**Calculation Example (gpt-5-mini):**
- Input: 8,000 tokens × $0.25 / 1M = $0.0020
- Output: 3,000 tokens × $2.00 / 1M = $0.0060
- Total: **$0.0080**

### Scenario 4: Enterprise Capture (5 GB PCAP)
**Compression:** 5 GB → ~35,000 tokens (analysis input)  
**Expected Output:** ~5,000 tokens

| Model | Input Cost | Output Cost | Total Cost |
|-------|------------|-------------|------------|
| **gpt-5-chat** | $0.0438 | $0.0500 | **$0.0938** |
| **gpt-5-mini** | $0.0088 | $0.0100 | **$0.0188** |
| **gpt-5-nano** | $0.0018 | $0.0020 | **$0.0038** |

**Calculation Example (gpt-5-mini):**
- Input: 35,000 tokens × $0.25 / 1M = $0.0088
- Output: 5,000 tokens × $2.00 / 1M = $0.0100
- Total: **$0.0188**

## Cost Optimization Tips

1. **Use gpt-5-chat** for reliable, high-quality analysis (recommended)
2. **Leverage focused analysis** with `--focus errors` or `--focus dns` to reduce tokens
3. **Pre-filter** PCAP files to focus on error-prone time windows
4. **Leverage caching** with Data Zone or Regional deployments for repeated analyses

## Key Takeaways

- **Recommended:** gpt-5-chat provides excellent, reliable analysis at ~$0.001-$0.01 per typical capture
- **Context Window:** 128K tokens - sufficient for most PCAP analyses
- **Data Zone Premium:** Add ~10% to costs for US/EU Data Zone deployments
- **Massive Savings:** Pre-processing reduces costs by >99.9% vs analyzing raw PCAP
- **Caching Benefit:** Use cached input pricing (90% discount) for repeated analyses
- **Quality Guarantee:** gpt-5-chat provides consistent, visible output (unlike some reasoning models)
