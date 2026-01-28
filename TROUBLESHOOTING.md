# Troubleshooting Guide

## Issue: "Insufficient credit" or "Request was throttled"

**Symptoms:**
```
[-] Cheap model failed: Fix generation failed: ReplicateError Details:
title: Insufficient credit
status: 402
```

**Root Cause:**
System environment variable `REPLICATE_API_TOKEN` is overriding the .env file with an old/invalid token.

**Solution:**

### Windows (PowerShell)
```powershell
# Check current system env
$env:REPLICATE_API_TOKEN

# If it shows an old token, update it:
$env:REPLICATE_API_TOKEN = "your_correct_token_from_env_file"

# Or remove it to use .env file:
Remove-Item Env:\REPLICATE_API_TOKEN
```

### Linux/Mac
```bash
# Check current system env
echo $REPLICATE_API_TOKEN

# If it shows an old token, update it:
export REPLICATE_API_TOKEN="your_correct_token_from_env_file"

# Or remove it to use .env file:
unset REPLICATE_API_TOKEN
```

### Permanent Fix
The system now prioritizes .env file over system environment variables (as of latest commit).

## Issue: JavaScript/TypeScript errors fail in sandbox

**Symptoms:**
```
Test failed: ExecutionError(name='SyntaxError', value="expected ':'")
```

**Root Cause:**
E2B sandbox currently only supports Python execution. JavaScript code is being run as Python.

**Status:**
- ✅ Multi-language parsing works (detects JS/TS errors correctly)
- ✅ Fix generation works (models generate correct JS/TS fixes)
- ❌ Sandbox testing only works for Python

**Workaround:**
For non-Python languages, the system will generate the fix but you'll need to manually verify it works.

## Issue: "No API token provided"

**Symptoms:**
```
ValueError: REPLICATE_API_TOKEN not found in environment
```

**Solution:**
1. Check `~/.timealready/.env` exists
2. Verify it contains: `REPLICATE_API_TOKEN=r8_...`
3. No quotes, no spaces around the `=`
4. Run: `timealready` to test

## Issue: Command not found: timealready

**Symptoms:**
```
bash: timealready: command not found
```

**Solution:**
```bash
# Reinstall
python -m pip install -e . --force-reinstall

# Or run directly
python timealready.py error.log
```

## Testing Your Setup

Run this test script:
```bash
python test_replicate.py
```

Expected output:
```
[*] API Token: r8_ULIEV0v...jo3J
[+] Client created successfully
[*] Testing API connection...
[*] Attempting to run a model...
[+] SUCCESS! Model responded: Hello! 😊
```

If you see "Insufficient credit", your token is wrong or has no credits.

## Verify Token is Correct

```bash
# Check .env file
cat ~/.timealready/.env

# Check system env (should be empty or match .env)
echo $REPLICATE_API_TOKEN  # Linux/Mac
$env:REPLICATE_API_TOKEN   # Windows

# Get your actual token from Replicate
# Go to: https://replicate.com/account/api-tokens
```

## Full Test

```bash
# Test with Python error (should work)
timealready test_project/error.log test_project

# Expected output:
# [*] Analyzing error...
# [!] Error: IndexError in test_project/utils.py:6
# [*] Generating fix with cheap model...
# [*] Testing fix in sandbox...
# [+] Fix works! Storing in memory...
# SUCCESS - FIX GENERATED
# Cost: $0.000200
```

## Still Having Issues?

1. Check Replicate account has credits: https://replicate.com/account/billing
2. Verify API token is active: https://replicate.com/account/api-tokens
3. Check rate limits (6 req/min without payment method)
4. Open an issue: https://github.com/justin55afdfdsf5ds45f4ds5f45ds4/timealready/issues
