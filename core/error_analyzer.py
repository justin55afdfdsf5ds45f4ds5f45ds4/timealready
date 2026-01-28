"""
Error Analyzer - Parses stack traces and extracts error information
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
        
        Extracts:
        - Error type and message
        - Stack trace with file paths and line numbers
        - The actual line that failed
        """
        lines = error_text.strip().split('\n')
        
        # Find error type and message (usually last line)
        error_line = lines[-1] if lines else ""
        error_match = re.match(r'(\w+(?:Error|Exception)):\s*(.+)', error_line)
        
        if not error_match:
            return None
        
        error_type = error_match.group(1)
        error_message = error_match.group(2)
        
        # Parse stack trace
        stack_frames = []
        current_file = None
        current_line = None
        
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
                    file=file_path,
                    line=line_num,
                    function=func_name,
                    code=code_line
                ))
                
                current_file = file_path
                current_line = line_num
        
        if not stack_frames:
            return None
        
        # The last frame is where the error occurred
        error_frame = stack_frames[-1]
        
        # Read the actual file content
        try:
            full_path = codebase_path / error_frame.file
            if full_path.exists():
                with open(full_path) as f:
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
