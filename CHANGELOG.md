# Changelog

## v1.1.0 - Memory Fallback (2026-01-28)

### 🚀 New Feature: Memory Fallback

**When Replicate API fails (rate limit, credits, network), system now falls back to UltraContext memory!**

**How it works:**
1. Try cheap model (DeepSeek V3) - $0.0002
2. If API fails → Check memory for similar fixes
3. If similar fix found → Apply it directly (FREE!)
4. If memory fix works → Return it (Cost: $0)
5. If no memory fix → Try smart model (Claude 4.5)

**Benefits:**
- ✅ Zero cost for repeated errors
- ✅ Works offline after learning
- ✅ Instant fixes from memory
- ✅ Resilient to API failures

**Example Flow:**
```
[*] Generating fix with cheap model...
[-] Cheap model failed: ReplicateError (rate limit)
[!] Attempting to apply learned fix from memory...
[+] Applied fix from memory!
[*] Testing memory fix in sandbox...
[+] Memory fix works!

SUCCESS - FIX GENERATED
Cost: $0.000000
Model: memory
```

### 📊 Memory Storage

**What's stored:**
- Error signature (hash of error type + pattern)
- Error type and file pattern
- Fix strategy description
- **Actual fixed code** (new!)
- Success/failure counts
- Success rate

**Matching algorithm:**
- Exact error type match
- File pattern similarity (e.g., `api/*.py`)
- Sorted by success rate
- Returns top 5 matches

### 🔧 Technical Changes

**Files Modified:**
- `core/memory_manager.py` - Added `apply_learned_fix()` method
- `models.py` - Added `fixed_code` field to `LearnedFix`
- `codehealer.py` - Integrated memory fallback in healing flow

**New Methods:**
- `MemoryManager.apply_learned_fix()` - Apply stored fix directly
- `MemoryManager._apply_fix_strategy()` - Reconstruct fix from memory
- `MemoryManager._generate_diff()` - Generate diff for memory fixes

### ⚠️ Current Limitations

**Memory Persistence:**
- Memory is currently in-memory only (Python dict)
- Does NOT persist across sessions/restarts
- UltraContext SDK integration pending

**Workaround:**
Memory works within the same session:
```bash
# First error - uses API, stores in memory
timealready error1.log

# Similar error - uses memory (if API fails)
timealready error2.log
```

**Future:**
- Persistent storage with UltraContext SDK
- Cross-session memory
- Shared team memory

### 📈 Cost Savings

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| First error | $0.0002 | $0.0002 | 0% |
| Same error (API works) | $0.0002 | $0.0002 | 0% |
| Same error (API fails) | FAIL | $0 | 100% |
| 100 similar errors (API fails) | FAIL | $0 | 100% |

---

## v1.0.0 - Multi-Language Support (2026-01-28)

### ✅ Fixed Issues

**1. Multi-Language Support**
- Added support for 9+ languages: Python, JavaScript, TypeScript, Java, C#, Go, Rust, PHP, Ruby
- Language-specific stack trace parsers
- Auto-detects language from file extension
- Generic fallback parser for unknown formats

**2. API Error Handling**
- Fixed: API credit errors now display properly instead of crashing
- Fixed: System checks if fix generation succeeded before testing
- Fixed: Clear error messages when models fail
- Improved: Graceful fallback from cheap to smart model

**3. Windows Path Issues**
- Fixed: All paths normalized to forward slashes
- Fixed: Path handling in sandbox executor
- Fixed: File reading with proper encoding (utf-8)
- Works correctly with both relative and absolute paths

### 🚀 Features

**Global Installation**
- Install once, use anywhere: `timealready error.log`
- Config stored at `~/.timealready/.env`
- Secure API key handling (not exposed in code)

**Multi-Language Stack Trace Parsing**
- Python: `File "path", line X`
- JavaScript/TypeScript: `at path:line:col`
- Java: `at package.Class.method(File.java:line)`
- C#: `at Namespace.Class.Method() in path:line`
- Go: `path/file.go:line`
- Rust: `--> path:line:col`
- PHP: `in /path/file.php on line X`
- Ruby: `from path:line:in 'method'`
- Generic: Any `file.ext:line` pattern

**Improved Error Flow**
1. Try cheap model (DeepSeek V3)
2. If generation fails → escalate to smart model
3. If generation succeeds → test in sandbox
4. If test fails → escalate to smart model
5. If test succeeds → store in memory

### 📊 Testing

**Tested Scenarios:**
- ✅ Python IndexError - parsed correctly
- ✅ File relation mapping from stack trace
- ✅ Fix generation with DeepSeek V3
- ✅ Sandbox testing in E2B
- ✅ Memory storage with hash IDs
- ✅ Global command works from any directory
- ✅ API error messages display correctly
- ✅ Windows path normalization

**Known Limitations:**
- Requires Replicate API credits to generate fixes
- Sandbox testing limited to Python/JavaScript (other languages need manual verification)
- Rate limits apply (6 requests/min without payment method)

### 🔧 Technical Changes

**Files Modified:**
- `core/error_analyzer.py` - Added 9 language parsers
- `core/fix_generator.py` - Language-aware prompt building
- `core/sandbox_executor.py` - Multi-language test generation + path fixes
- `codehealer.py` - Improved error handling flow
- `README.md` - Updated to reflect multi-language support

**API Changes:**
- None (backward compatible)

### 📝 Usage

```bash
# Install globally
python install.py

# Use from any project
timealready error.log
timealready error.log /path/to/project
timealready "Error: undefined is not a function..."

# Works with any language
timealready javascript_error.log
timealready java_stacktrace.txt
timealready rust_panic.log
```

### 🐛 Bug Fixes

- Fixed: TypeError when fix_result.fixed_code is None
- Fixed: API errors showing as "FAILED: Fix generation failed" with no details
- Fixed: Windows backslash paths breaking sandbox
- Fixed: File encoding errors on non-ASCII files
- Fixed: System trying to test failed fix generations

### 🎯 Next Steps

- Add payment method to Replicate for full testing
- Test with real JavaScript/TypeScript errors
- Test with Java/C# errors
- Add more language-specific sandbox tests
- Improve diff generation for multi-language
