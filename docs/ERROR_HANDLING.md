# Error Handling Documentation

## Overview

The pcap-ai-analyzer tools include error handling for common failure scenarios. This document describes error types, their meanings, and troubleshooting steps.

## Exit Codes

All scripts use standard exit codes:

- **0** - Success
- **1** - General error (file not found, invalid input, API errors, etc.)
- **130** - User interrupted (Ctrl+C)

## Error Scenarios by Tool

### sanitize_pcap.py

#### File Errors

**Error: Input file not found**
```
❌ Error: Input file not found: example.cap
```
- **Cause**: The specified input PCAP file doesn't exist
- **Solution**: Check the file path and ensure the file exists
- **Exit Code**: 1

**Error: Input file is empty**
```
❌ Error: Input file is empty (0 bytes)
```
- **Cause**: The input file exists but contains no data
- **Solution**: Verify the file was captured correctly or use a different file
- **Exit Code**: 1

**Error: Cannot read input file**
```
❌ Error: Cannot read input file (permission denied): example.cap
```
- **Cause**: Insufficient permissions to read the input file
- **Solution**: Check file permissions with `ls -l` and use `chmod` if needed
- **Exit Code**: 1

**Error: Cannot write to output directory**
```
❌ Error: Cannot write to output directory (permission denied): /path/to/output
```
- **Cause**: Insufficient permissions to write to the output directory
- **Solution**: Check directory permissions or choose a different output location
- **Exit Code**: 1

#### Format Errors

**Error: Invalid or corrupted PCAP file**
```
❌ Error: Invalid or corrupted PCAP file: example.cap (Not a supported capture file)
```
- **Cause**: File is not a valid PCAP/PCAPNG format or is corrupted
- **Solution**: 
  - Verify the file is actually a PCAP file
  - Try opening it in Wireshark to confirm it's valid
  - Re-capture the network traffic if corrupted
- **Exit Code**: 1

**Error: Corrupted PCAP file (truncated)**
```
❌ Error: Corrupted or truncated PCAP file: example.cap
```
- **Cause**: File was not completely written (transfer interrupted, disk full during capture)
- **Solution**: Use the partial data if valuable, or re-capture
- **Exit Code**: 1

#### Resource Errors

**Error: No space left on device**
```
❌ Error: Failed to write sanitized PCAP: [Errno 28] No space left on device
```
- **Cause**: Output disk is full
- **Solution**: Free up disk space or write to a different location
- **Exit Code**: 1

**Error: Disk quota exceeded**
```
❌ Error: Failed to write sanitized PCAP: [Errno 122] Disk quota exceeded
```
- **Cause**: User disk quota limit reached
- **Solution**: Remove unnecessary files or request quota increase
- **Exit Code**: 1

#### Packet Processing Errors

**Warning: Error processing packet**
```
⚠️  Warning: Error processing packet #42: [error details]
```
- **Cause**: Individual packet is malformed or contains unexpected data
- **Impact**: The problematic packet is skipped, processing continues
- **Note**: Tool tolerates up to 100 packet errors before aborting
- **Exit Code**: Continues (only exits if >100 errors)

### prepare_for_ai_analysis.py

#### Input Errors

**Error: PCAP file not found**
```
❌ Error: PCAP file not found: example.cap
```
- **Cause**: Input file doesn't exist
- **Solution**: Verify the file path
- **Exit Code**: 1

**Error: No valid packets found**
```
❌ Error: No valid packets found in PCAP file: example.cap
```
- **Cause**: PCAP file is valid but contains no analyzable packets
- **Solution**: Check if the file captured actual network traffic
- **Exit Code**: 1

**Error: Invalid or corrupted PCAP file format**
```
❌ Error: Failed to load PCAP file: Invalid or corrupted PCAP file format
```
- **Cause**: File format is invalid or corrupted
- **Solution**: Validate the PCAP file with Wireshark or tcpdump
- **Exit Code**: 1

#### Output Errors

**Error: Parent directory does not exist**
```
❌ Error: Parent directory does not exist: /nonexistent/path
```
- **Cause**: The parent directory for the output location doesn't exist
- **Solution**: Create parent directories first or use an existing path
- **Exit Code**: 1

**Error: Cannot write to output directory**
```
❌ Error: Cannot write to output directory (permission denied): analysis/
```
- **Cause**: Insufficient permissions
- **Solution**: Check directory permissions or choose a writable location
- **Exit Code**: 1

#### Memory Errors

**Error: Out of memory**
```
❌ Error: Out of memory while processing PCAP file (file too large)
   Try splitting the file into smaller chunks using 'editcap'
```
- **Cause**: PCAP file is too large to fit in available memory
- **Solution**: Split the file using:
  ```bash
  editcap -c 100000 large.cap split.cap
  ```
  This creates multiple files with 100,000 packets each
- **Exit Code**: 1

### analyze_with_ai.py

#### Directory Errors

**Error: Analysis directory not found**
```
❌ Error: Analysis directory not found: ai_analysis
```
- **Cause**: The specified analysis directory doesn't exist
- **Solution**: Run `prepare_for_ai_analysis.py` first to create the analysis files
- **Exit Code**: 1

**Error: Path is not a directory**
```
❌ Error: Path is not a directory: file.txt
```
- **Cause**: Specified path is a file, not a directory
- **Solution**: Provide a directory path, not a file
- **Exit Code**: 1

**Error: Missing required analysis files**
```
❌ Error: Missing required analysis files in ai_analysis: summary.json, errors_detailed.json
Run 'prepare_for_ai_analysis.py' first to generate these files.
```
- **Cause**: Analysis directory exists but doesn't contain required files
- **Solution**: Run `prepare_for_ai_analysis.py` to generate the required files
- **Exit Code**: 1

#### Credential Errors

**Error: Azure OpenAI endpoint not found**
```
❌ Error: Azure OpenAI endpoint not found.
Set AZURE_OPENAI_ENDPOINT environment variable or add to .env file
```
- **Cause**: AZURE_OPENAI_ENDPOINT environment variable is not set
- **Solution**: 
  ```bash
  export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
  ```
  Or add to `.env` file
- **Exit Code**: 1

**Error: Azure OpenAI API key not found**
```
❌ Error: Azure OpenAI API key not found.
Set AZURE_OPENAI_API_KEY environment variable or add to .env file
```
- **Cause**: AZURE_OPENAI_API_KEY environment variable is not set
- **Solution**:
  ```bash
  export AZURE_OPENAI_API_KEY="your-api-key-here"
  ```
  Or add to `.env` file
- **Exit Code**: 1

**Error: Invalid endpoint URL format**
```
❌ Error: Invalid endpoint URL format: invalid-url
```
- **Cause**: Endpoint URL doesn't start with http:// or https://
- **Solution**: Use proper URL format: `https://your-resource.openai.azure.com`
- **Exit Code**: 1

#### API Errors

**Error: Authentication failed**
```
❌ Error: Authentication failed: [error details]
  Check your AZURE_OPENAI_API_KEY
```
- **Cause**: Invalid or expired API key
- **Solution**: Verify API key in Azure Portal and update environment variable
- **Exit Code**: 1

**Error: Cannot connect to Azure OpenAI**
```
❌ Error: Cannot connect to Azure OpenAI: [error details]
  Check your network connection and endpoint URL
```
- **Cause**: Network connectivity issues or invalid endpoint
- **Solution**: 
  - Check internet connection
  - Verify endpoint URL is correct
  - Check firewall settings
- **Exit Code**: 1

**Error: Request timed out**
```
❌ Error: Request timed out: [error details]
  The API may be overloaded or your network is slow
```
- **Cause**: Request took too long to complete
- **Solution**: 
  - Try again after a few minutes
  - Check network speed
  - Consider using a smaller focus area
- **Exit Code**: 1

**Error: Rate limit exceeded**
```
❌ Error: Rate limit exceeded: [error details]
  Wait a moment and try again
```
- **Cause**: Too many requests in a short time period
- **Solution**: Wait 30-60 seconds before retrying
- **Exit Code**: 1

**Error: Quota exceeded**
```
❌ Error: Quota exceeded: [error details]
  Check your Azure OpenAI quota and billing
```
- **Cause**: Azure OpenAI service quota limit reached
- **Solution**: 
  - Check Azure Portal for quota status
  - Verify billing is active
  - Request quota increase if needed
- **Exit Code**: 1

## Interruption Handling

All tools handle Ctrl+C (SIGINT) gracefully:

```
❌ Operation cancelled by user
```

- **Behavior**: Clean up partial output files where applicable
- **Exit Code**: 130

## Best Practices

### 1. Check File Validity First
Before processing, verify your PCAP file:
```bash
capinfos input.pcap
```

### 2. Validate Permissions
Ensure you have proper permissions:
```bash
ls -l input.pcap           # Check read permission
ls -ld output_directory/    # Check write permission
```

### 3. Monitor Disk Space
Check available space before processing large files:
```bash
df -h .
```

### 4. Use Test Files First
Test with small PCAP files before processing large ones:
```bash
editcap -c 1000 large.cap small.cap  # Extract first 1000 packets
```

### 5. Validate Environment Variables
Check Azure OpenAI credentials are set:
```bash
echo $AZURE_OPENAI_ENDPOINT
echo $AZURE_OPENAI_API_KEY | head -c 10  # Show first 10 chars
```

### 6. Review Logs
Pay attention to warnings - they may indicate data quality issues:
```
⚠️  Warning: Error processing packet #42
```

## Troubleshooting Workflow

1. **Check Exit Code**
   ```bash
   echo $?  # After running a script
   ```

2. **Look for Specific Error Messages**
   - Read the error message carefully
   - Note the error type (file not found, permission, format, etc.)

3. **Verify Prerequisites**
   - File exists and is readable
   - Output location is writable
   - Environment variables are set (for analyze_with_ai.py)

4. **Try with Smaller Data**
   - Use a subset of packets to isolate the issue

5. **Check System Resources**
   - Disk space: `df -h`
   - Memory: `free -h`
   - Permissions: `ls -l`

## Testing Error Handling

A test suite is included:

```bash
cd pcap-ai-analyzer
./tests/test_error_scenarios.sh
```

This tests common error scenarios.

## Getting Help

If you encounter an error not documented here:

1. Check if it's a known issue in the GitHub repository
2. Try running with a minimal test case
3. Include the full error message when seeking help
4. Note your environment (OS, Python version, file size)

## Error Handling Approach

The tools follow these principles:

1. **Early Detection**: Check for errors before processing
2. **Clear Messages**: Explain what went wrong and how to fix it
3. **Standard Exit Codes**: Enable scripting and automation
4. **Continue When Possible**: Skip problematic packets when feasible
5. **Clean Interruption**: Handle Ctrl+C without leaving partial files
6. **Input Validation**: Validate inputs before processing
