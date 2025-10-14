# Tests

This directory contains test scripts for the PCAP AI Analyzer project.

## Test Scripts

### Error Handling Tests
- **[test_error_scenarios.sh](test_error_scenarios.sh)** - Comprehensive error handling test suite
  - Tests 23+ error scenarios across all tools
  - Validates file handling, permissions, formats, and API errors
  - Checks exit codes and error messages

## Running Tests

### Run Error Handling Tests
```bash
cd pcap-ai-analyzer
./tests/test_error_scenarios.sh
```

Expected output:
```
============================================================
ERROR HANDLING TEST SUITE FOR PCAP-AI-ANALYZER
============================================================

Testing all scripts...

✓ PASS: sanitize_pcap: Missing input file error detected
✓ PASS: sanitize_pcap: Invalid format detected
...
============================================================
TEST SUMMARY
============================================================
Passed: 23
Failed: 0
Total: 23

✅ ALL TESTS PASSED!
```

## Test Coverage

The test suite covers:
- **File Handling**: Missing files, empty files, invalid formats
- **Permissions**: Read/write permission errors
- **Data Validation**: Corrupted PCAPs, empty data
- **Command Line**: Invalid arguments, missing required parameters
- **API Integration**: Missing credentials, invalid endpoints
- **Exit Codes**: Proper error code reporting

## Adding New Tests

When adding tests:
1. Follow the existing test pattern in `test_error_scenarios.sh`
2. Use descriptive test names
3. Check for expected error messages
4. Validate exit codes
5. Clean up test files after execution

Example:
```bash
echo "=== Test X: Description ==="
python3 script.py --invalid-option 2>&1 | grep -q "error"
test_result $? "script: Description of what's tested"
```

## Test Environment

Tests run in isolation and don't require:
- Azure OpenAI credentials (mocked where needed)
- Real PCAP files (creates test files)
- External dependencies (beyond Python requirements)

## Contributing

See [../CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing tests.
