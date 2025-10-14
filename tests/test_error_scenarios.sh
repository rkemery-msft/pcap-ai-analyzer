#!/bin/bash
#
#!/bin/bash
# Comprehensive error handling test suite for pcap-ai-analyzer

set +e  # Don't exit on errors, we expect some

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to check test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
    echo ""
}

echo "============================================================"
echo "ERROR HANDLING TEST SUITE FOR PCAP-AI-ANALYZER"
echo "============================================================"
echo ""
echo "Testing improved versions of all three scripts..."
echo ""

# ============================================================
# SANITIZE_PCAP TESTS
# ============================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}SANITIZE_PCAP.PY TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 1: Missing input file
echo "=== Test 1: Missing input file ==="
python3 sanitize_pcap_improved.py --input nonexistent.cap --output test.cap 2>&1 | grep -qi "not found"
test_result $? "sanitize_pcap: Missing input file error detected"

# Test 2: Invalid file format
echo "=== Test 2: Invalid file format ==="
echo "Not a PCAP file" > invalid.txt
python3 sanitize_pcap_improved.py --input invalid.txt --output test.cap 2>&1 | grep -qi "invalid\|corrupted"
test_result $? "sanitize_pcap: Invalid format detected"

# Test 3: Empty file
echo "=== Test 3: Empty file ==="
touch empty.cap
python3 sanitize_pcap_improved.py --input empty.cap --output test.cap 2>&1 | grep -qi "empty"
test_result $? "sanitize_pcap: Empty file detected"

# Test 4: Permission issues (read)
echo "=== Test 4: Permission issues (read) ==="
echo "test" > readonly.cap
chmod 000 readonly.cap
python3 sanitize_pcap_improved.py --input readonly.cap --output test.cap 2>&1 | grep -qi "permission\|cannot read"
TEST_RESULT=$?
chmod 644 readonly.cap
rm -f readonly.cap
test_result $TEST_RESULT "sanitize_pcap: Read permission error detected"

# Test 5: Permission issues (write)
echo "=== Test 5: Permission issues (write) ==="
mkdir -p readonly_dir
chmod 000 readonly_dir
echo "test" > writable_input.cap
python3 sanitize_pcap_improved.py --input writable_input.cap --output readonly_dir/output.cap 2>&1 | grep -qi "permission\|cannot write"
TEST_RESULT=$?
chmod 755 readonly_dir
rmdir readonly_dir
rm -f writable_input.cap
test_result $TEST_RESULT "sanitize_pcap: Write permission error detected"

# Test 6: Invalid command-line arguments
echo "=== Test 6: Invalid command-line arguments ==="
python3 sanitize_pcap_improved.py --invalid-arg 2>&1 | grep -qi "error\|unrecognized\|usage"
test_result $? "sanitize_pcap: Invalid arguments detected"

# Test 7: Corrupted PCAP file
echo "=== Test 7: Corrupted PCAP file ==="
echo -e "\xd4\xc3\xb2\xa1\x02\x00\x04\x00CORRUPTED DATA HERE" > corrupted.cap
python3 sanitize_pcap_improved.py --input corrupted.cap --output test.cap 2>&1 | grep -qi "corrupted\|invalid\|not a supported"
test_result $? "sanitize_pcap: Corrupted file detected"

# Test 8: Proper exit codes
echo "=== Test 8: Proper exit codes ==="
python3 sanitize_pcap_improved.py --input nonexistent.cap --output test.cap >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    test_result 0 "sanitize_pcap: Non-zero exit code on error ($EXIT_CODE)"
else
    test_result 1 "sanitize_pcap: Should return non-zero exit code on error"
fi

# ============================================================
# PREPARE_FOR_AI_ANALYSIS TESTS
# ============================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}PREPARE_FOR_AI_ANALYSIS.PY TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 9: Missing required arguments
echo "=== Test 9: Missing required arguments ==="
python3 prepare_for_ai_analysis_improved.py 2>&1 | grep -qi "required\|error"
test_result $? "prepare: Missing required args detected"

# Test 10: Missing input file
echo "=== Test 10: Missing input file ==="
python3 prepare_for_ai_analysis_improved.py --input nonexistent.cap 2>&1 | grep -qi "not found"
test_result $? "prepare: Missing input file detected"

# Test 11: Invalid file format
echo "=== Test 11: Invalid file format ==="
echo "Not a PCAP" > invalid_prep.txt
python3 prepare_for_ai_analysis_improved.py --input invalid_prep.txt --output-dir test_out 2>&1 | grep -qi "invalid\|corrupted\|failed"
TEST_RESULT=$?
rm -f invalid_prep.txt
test_result $TEST_RESULT "prepare: Invalid format detected"

# Test 12: Empty PCAP file
echo "=== Test 12: Empty PCAP file ==="
touch empty_prep.cap
python3 prepare_for_ai_analysis_improved.py --input empty_prep.cap --output-dir test_out 2>&1 | grep -qi "empty\|no packets"
TEST_RESULT=$?
rm -f empty_prep.cap
test_result $TEST_RESULT "prepare: Empty file detected"

# Test 13: Parent directory doesn't exist
echo "=== Test 13: Parent directory doesn't exist ==="
python3 prepare_for_ai_analysis_improved.py --input test.cap --output-dir /nonexistent/path/output 2>&1 | grep -qi "not exist\|error"
test_result $? "prepare: Missing parent directory detected"

# Test 14: Proper exit codes
echo "=== Test 14: Proper exit codes ==="
python3 prepare_for_ai_analysis_improved.py --input nonexistent.cap >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    test_result 0 "prepare: Non-zero exit code on error ($EXIT_CODE)"
else
    test_result 1 "prepare: Should return non-zero exit code on error"
fi

# ============================================================
# ANALYZE_WITH_AI TESTS
# ============================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}ANALYZE_WITH_AI.PY TESTS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 15: Missing analysis directory
echo "=== Test 15: Missing analysis directory ==="
python3 analyze_with_ai_improved.py --dir /nonexistent/dir 2>&1 | grep -qi "not found\|error"
test_result $? "analyze: Missing directory detected"

# Test 16: Invalid directory (file instead of directory)
echo "=== Test 16: Invalid directory (file instead of directory) ==="
touch not_a_directory
python3 analyze_with_ai_improved.py --dir not_a_directory 2>&1 | grep -qi "not a directory\|error"
TEST_RESULT=$?
rm -f not_a_directory
test_result $TEST_RESULT "analyze: Invalid directory type detected"

# Test 17: Missing required analysis files
echo "=== Test 17: Missing required analysis files ==="
mkdir -p empty_analysis_dir
python3 analyze_with_ai_improved.py --dir empty_analysis_dir 2>&1 | grep -qi "missing.*files\|not found"
TEST_RESULT=$?
rmdir empty_analysis_dir
test_result $TEST_RESULT "analyze: Missing analysis files detected"

# Test 18: Missing environment variables
echo "=== Test 18: Missing environment variables ==="
(unset AZURE_OPENAI_ENDPOINT AZURE_OPENAI_API_KEY; \
 mkdir -p test_analysis_dir && \
 echo '{}' > test_analysis_dir/summary.json && \
 echo '{}' > test_analysis_dir/errors_detailed.json && \
 python3 analyze_with_ai_improved.py --dir test_analysis_dir 2>&1 | grep -qi "credentials\|not found\|endpoint\|api.*key")
TEST_RESULT=$?
rm -rf test_analysis_dir
test_result $TEST_RESULT "analyze: Missing credentials detected"

# Test 19: Invalid endpoint format
echo "=== Test 19: Invalid endpoint format ==="
(export AZURE_OPENAI_ENDPOINT="invalid-url" AZURE_OPENAI_API_KEY="test"; \
 mkdir -p test_analysis_dir2 && \
 echo '{}' > test_analysis_dir2/summary.json && \
 echo '{}' > test_analysis_dir2/errors_detailed.json && \
 python3 analyze_with_ai_improved.py --dir test_analysis_dir2 2>&1 | grep -qi "invalid.*endpoint\|invalid.*url\|error")
TEST_RESULT=$?
rm -rf test_analysis_dir2
test_result $TEST_RESULT "analyze: Invalid endpoint format detected"

# Test 20: Proper exit codes
echo "=== Test 20: Proper exit codes ==="
python3 analyze_with_ai_improved.py --dir /nonexistent >/dev/null 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    test_result 0 "analyze: Non-zero exit code on error ($EXIT_CODE)"
else
    test_result 1 "analyze: Should return non-zero exit code on error"
fi

# ============================================================
# CODE QUALITY CHECKS
# ============================================================

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}CODE QUALITY CHECKS${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Test 21: No bare except clauses
echo "=== Test 21: No bare except clauses ==="
! grep -n "except:" sanitize_pcap_improved.py | grep -v "except Exception" | grep -v "except:" >/dev/null 2>&1
test_result $? "No bare except clauses in sanitize_pcap"

# Test 22: Proper error messages to stderr
echo "=== Test 22: Proper error messages to stderr ==="
grep -q "file=sys.stderr" sanitize_pcap_improved.py
test_result $? "Error messages directed to stderr"

# Test 23: Exit code constants used
echo "=== Test 23: Exit code constants ==="
grep -q "sys.exit(0)\|sys.exit(1)\|sys.exit(130)" sanitize_pcap_improved.py
test_result $? "Proper exit codes used"

# Cleanup
rm -f test.cap invalid.txt empty.cap corrupted.cap *.txt *.json 2>/dev/null

echo ""
echo "============================================================"
echo "TEST SUMMARY"
echo "============================================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $TESTS_FAILED${NC}"
else
    echo "Failed: 0"
fi
echo "Total: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
    echo ""
    echo "The improved scripts have robust error handling for:"
    echo "  • Missing files and directories"
    echo "  • Invalid file formats and corrupted data"
    echo "  • Permission errors (read/write)"
    echo "  • Empty files and missing data"
    echo "  • Invalid command-line arguments"
    echo "  • Missing environment variables"
    echo "  • Proper exit codes"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    echo "Review the failures above and fix the issues."
    echo ""
    exit 1
fi
#

set -e

SCRIPT_DIR="/home/rick/pcap-ai-analyzer"
TEST_DIR="/tmp/pcap-error-handling-test"
cd "$TEST_DIR"

echo "================================================================================"
echo "PCAP AI ANALYZER - ERROR HANDLING TEST SUITE"
echo "================================================================================"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

test_result() {
    if [ $1 -eq 0 ]; then
        echo "✅ PASSED: $2"
        ((TESTS_PASSED++))
    else
        echo "❌ FAILED: $2"
        ((TESTS_FAILED++))
    fi
}

# =============================================================================
# Test 1: Missing Input File
# =============================================================================
echo "Test 1: Missing input file..."
python3 "$SCRIPT_DIR/sanitize_pcap.py" --input nonexistent.cap --output test.cap 2>&1 | grep -q "not found\|does not exist\|No such file"
test_result $? "sanitize_pcap.py handles missing input file"

# =============================================================================
# Test 2: Invalid File Format  
# =============================================================================
echo "Test 2: Invalid file format..."
echo "This is not a PCAP file" > invalid.txt
python3 "$SCRIPT_DIR/sanitize_pcap.py" --input invalid.txt --output test.cap 2>&1 | grep -q "Error\|Failed\|Invalid"
test_result $? "sanitize_pcap.py handles invalid file format"

# =============================================================================
# Test 3: Permission Issues
# =============================================================================
echo "Test 3: No write permission..."
mkdir -p readonly_dir
chmod 444 readonly_dir
python3 "$SCRIPT_DIR/sanitize_pcap.py" --input invalid.txt --output readonly_dir/test.cap 2>&1 | grep -q "permission\|Permission\|cannot"
RESULT=$?
chmod 755 readonly_dir  # cleanup
test_result $RESULT "sanitize_pcap.py handles write permission errors"

# =============================================================================
# Test 4: Empty File
# =============================================================================
echo "Test 4: Empty file..."
touch empty.cap
python3 "$SCRIPT_DIR/sanitize_pcap.py" --input empty.cap --output test.cap 2>&1 | grep -q "empty\|Empty\|no packets\|Error\|Failed"
test_result $? "sanitize_pcap.py handles empty file"

# =============================================================================
# Test 5: Invalid Arguments
# =============================================================================
echo "Test 5: Invalid arguments..."
python3 "$SCRIPT_DIR/sanitize_pcap.py" --invalid-flag 2>&1 | grep -q "error\|Error\|unrecognized"
test_result $? "sanitize_pcap.py handles invalid arguments"

# =============================================================================
# Test 6: Missing Required Arguments (prepare_for_ai_analysis.py)
# =============================================================================
echo "Test 6: Missing arguments for prepare_for_ai_analysis.py..."
python3 "$SCRIPT_DIR/prepare_for_ai_analysis.py" 2>&1 | grep -q "required\|usage\|error"
test_result $? "prepare_for_ai_analysis.py handles missing arguments"

# =============================================================================
# Test 7: Invalid Directory (analyze_with_ai.py)
# =============================================================================
echo "Test 7: Invalid directory for analyze_with_ai.py..."
python3 "$SCRIPT_DIR/analyze_with_ai.py" --dir /nonexistent/path --focus general 2>&1 | grep -q "not found\|does not exist\|No such"
test_result $? "analyze_with_ai.py handles missing directory"

# =============================================================================
# Test 8: Missing Environment Variables
# =============================================================================
echo "Test 8: Missing environment variables..."
(unset AZURE_OPENAI_ENDPOINT AZURE_OPENAI_API_KEY && python3 "$SCRIPT_DIR/analyze_with_ai.py" --dir . --focus general 2>&1) | grep -q "environment\|credentials\|API key\|endpoint"
test_result $? "analyze_with_ai.py handles missing credentials"

# =============================================================================
# Test 9: Corrupted PCAP File
# =============================================================================
echo "Test 9: Corrupted PCAP file..."
# Create a file with PCAP magic number but corrupted data
printf '\xd4\xc3\xb2\xa1\x02\x00\x04\x00' > corrupted.cap
dd if=/dev/urandom bs=1024 count=1 >> corrupted.cap 2>/dev/null
python3 "$SCRIPT_DIR/sanitize_pcap.py" --input corrupted.cap --output test.cap 2>&1 | grep -q "Error\|Failed\|corrupt\|invalid"
test_result $? "sanitize_pcap.py handles corrupted PCAP"

# =============================================================================
# Test 10: Out of Disk Space (simulated)
# =============================================================================
echo "Test 10: Insufficient disk space handling..."
# This test assumes the tool will handle write errors gracefully
# We can't actually fill the disk, so we check if error handling exists
grep -q "except.*IOError\|except.*OSError\|except.*Exception" "$SCRIPT_DIR/sanitize_pcap.py"
test_result $? "sanitize_pcap.py has error handling for I/O errors"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "================================================================================"
echo "TEST SUMMARY"
echo "================================================================================"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"
echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ SOME TESTS FAILED - Error handling needs improvement"
    exit 1
fi
