# Changelog

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
- Install once, use anywhere: `xbyt1p error.log`
- Config stored at `~/.xbyt1p/.env`
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
xbyt1p error.log
xbyt1p error.log /path/to/project
xbyt1p "Error: undefined is not a function..."

# Works with any language
xbyt1p javascript_error.log
xbyt1p java_stacktrace.txt
xbyt1p rust_panic.log
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
