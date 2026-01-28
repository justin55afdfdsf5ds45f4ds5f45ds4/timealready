"""
Error Analyzer - Parses stack traces and extracts error information
Supports: Python, JavaScript, TypeScript, Java, C#, Go, Rust, PHP, Ruby
"""
import re
from pathlib import Path
from typing import Optional
from models import ErrorReport, StackFrame


class ErrorAnalyzer:
    """Parses error logs and extracts structured information"""
    
    def parse(self, error_text: str, codebase_path: Path) -> Optional[ErrorReport]:
        """
        Parse error text (stack trace) into structured ErrorReport.
        
        Supports multiple languages by detecting patterns:
        - Python: File "path", line X
        - JavaScript/TypeScript: at path:line:col
        - Java: at package.Class.method(File.java:line)
        - C#: at Namespace.Class.Method() in path:line line
        - Go: path/file.go:line
        - Rust: --> path:line:col
        - PHP: in /path/file.php on line X
        - Ruby: from path:line:in `method'
        """
        lines = error_text.strip().split('\n')
        
        # Try to detect language and parse accordingly
        if 'File "' in error_text or 'Traceback' in error_text:
            return self._parse_python(lines, codebase_path)
        elif ' at ' in error_text and ('.js:' in error_text or '.ts:' in error_text):
            return self._parse_javascript(lines, codebase_path)
        elif '.java:' in error_text and ' at ' in error_text:
            return self._parse_java(lines, codebase_path)
        elif '.cs:line' in error_text or '.cs: line' in error_text:
            return self._parse_csharp(lines, codebase_path)
        elif '.go:' in error_text:
            return self._parse_go(lines, codebase_path)
        elif '-->' in error_text and '.rs:' in error_text:
            return self._parse_rust(lines, codebase_path)
        elif '.php on line' in error_text or '.php:' in error_text:
            return self._parse_php(lines, codebase_path)
        elif '.rb:' in error_text and 'from ' in error_text:
            return self._parse_ruby(lines, codebase_path)
        else:
            # Generic fallback
            return self._parse_generic(lines, codebase_path)
    
    def _parse_python(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse Python stack traces"""
        # Find error type and message (usually last line)
        error_line = lines[-1] if lines else ""
        error_match = re.match(r'(\w+(?:Error|Exception)):\s*(.+)', error_line)
        
        if not error_match:
            return None
        
        error_type = error_match.group(1)
        error_message = error_match.group(2)
        
        # Parse stack trace
        stack_frames = []
        
        for i, line in enumerate(lines):
            # Match: File "path/to/file.py", line 123, in function_name
            file_match = re.search(r'File "([^"]+)", line (\d+)', line)
            if file_match:
                file_path = file_match.group(1)
                line_num = int(file_match.group(2))
                
                # Get function name if available
                func_match = re.search(r'in (\w+)', line)
                func_name = func_match.group(1) if func_match else None
                
                # Get the actual code line (usually next line)
                code_line = lines[i+1].strip() if i+1 < len(lines) else None
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=func_name,
                    code=code_line
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_javascript(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse JavaScript/TypeScript stack traces"""
        # Find error type and message (usually first line)
        error_line = lines[0] if lines else ""
        error_match = re.match(r'(\w+(?:Error|Exception)):\s*(.+)', error_line)
        
        if not error_match:
            error_type = "Error"
            error_message = error_line
        else:
            error_type = error_match.group(1)
            error_message = error_match.group(2)
        
        stack_frames = []
        
        for line in lines:
            # Match: at functionName (path/file.js:123:45)
            # or: at path/file.js:123:45
            match = re.search(r'at (?:(\w+) )?\(?([^:]+):(\d+):(\d+)\)?', line)
            if match:
                func_name = match.group(1)
                file_path = match.group(2)
                line_num = int(match.group(3))
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=func_name,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_java(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse Java stack traces"""
        error_line = lines[0] if lines else ""
        error_match = re.match(r'(\w+(?:Exception|Error)):\s*(.+)', error_line)
        
        if not error_match:
            return None
        
        error_type = error_match.group(1)
        error_message = error_match.group(2)
        
        stack_frames = []
        
        for line in lines:
            # Match: at package.Class.method(File.java:123)
            match = re.search(r'at ([\w.]+)\(([^:]+):(\d+)\)', line)
            if match:
                func_name = match.group(1)
                file_path = match.group(2)
                line_num = int(match.group(3))
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=func_name,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_csharp(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse C# stack traces"""
        error_line = lines[0] if lines else ""
        error_match = re.match(r'(\w+(?:Exception)):\s*(.+)', error_line)
        
        if not error_match:
            return None
        
        error_type = error_match.group(1)
        error_message = error_match.group(2)
        
        stack_frames = []
        
        for line in lines:
            # Match: at Namespace.Class.Method() in path\file.cs:line 123
            match = re.search(r'at ([\w.]+)\(\) in ([^:]+):line (\d+)', line)
            if match:
                func_name = match.group(1)
                file_path = match.group(2)
                line_num = int(match.group(3))
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=func_name,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_go(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse Go stack traces"""
        error_line = lines[0] if lines else ""
        error_type = "Error"
        error_message = error_line
        
        stack_frames = []
        
        for line in lines:
            # Match: path/file.go:123
            match = re.search(r'([^\s]+\.go):(\d+)', line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=None,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_rust(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse Rust stack traces"""
        error_line = lines[0] if lines else ""
        error_type = "Error"
        error_message = error_line
        
        stack_frames = []
        
        for line in lines:
            # Match: --> path/file.rs:123:45
            match = re.search(r'--> ([^:]+):(\d+):(\d+)', line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=None,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_php(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse PHP stack traces"""
        error_line = lines[0] if lines else ""
        error_match = re.match(r'(\w+(?:Error|Exception)):\s*(.+)', error_line)
        
        if not error_match:
            error_type = "Error"
            error_message = error_line
        else:
            error_type = error_match.group(1)
            error_message = error_match.group(2)
        
        stack_frames = []
        
        for line in lines:
            # Match: in /path/file.php on line 123
            match = re.search(r'in ([^:]+\.php) on line (\d+)', line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=None,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_ruby(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Parse Ruby stack traces"""
        error_line = lines[0] if lines else ""
        error_match = re.match(r'(\w+(?:Error|Exception)):\s*(.+)', error_line)
        
        if not error_match:
            error_type = "Error"
            error_message = error_line
        else:
            error_type = error_match.group(1)
            error_message = error_match.group(2)
        
        stack_frames = []
        
        for line in lines:
            # Match: from path/file.rb:123:in `method'
            match = re.search(r'from ([^:]+):(\d+):in `([^\']+)\'', line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                func_name = match.group(3)
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=func_name,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _parse_generic(self, lines: list, codebase_path: Path) -> Optional[ErrorReport]:
        """Generic parser for unknown formats"""
        error_line = lines[0] if lines else ""
        error_type = "Error"
        error_message = error_line
        
        stack_frames = []
        
        # Try to find any file:line patterns
        for line in lines:
            match = re.search(r'([^\s:]+\.\w+):(\d+)', line)
            if match:
                file_path = match.group(1)
                line_num = int(match.group(2))
                
                stack_frames.append(StackFrame(
                    file=self._normalize_path(file_path),
                    line=line_num,
                    function=None,
                    code=None
                ))
        
        if not stack_frames:
            return None
        
        return self._build_error_report(
            error_type, error_message, stack_frames, codebase_path
        )
    
    def _normalize_path(self, file_path: str) -> str:
        """Normalize file path to use forward slashes"""
        return file_path.replace('\\', '/')
    
    def _build_error_report(
        self,
        error_type: str,
        error_message: str,
        stack_frames: list,
        codebase_path: Path
    ) -> ErrorReport:
        """Build ErrorReport from parsed data"""
        # The last frame is where the error occurred
        error_frame = stack_frames[-1]
        
        # Read the actual file content
        try:
            full_path = codebase_path / error_frame.file
            if full_path.exists():
                with open(full_path, encoding='utf-8', errors='ignore') as f:
                    file_content = f.read()
            else:
                file_content = None
        except:
            file_content = None
        
        return ErrorReport(
            error_type=error_type,
            error_message=error_message,
            file_path=error_frame.file,
            line_number=error_frame.line,
            function_name=error_frame.function,
            stack_trace=stack_frames,
            file_content=file_content
        )
