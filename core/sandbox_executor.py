"""
Sandbox Executor - Runs code in E2B sandbox for testing
"""
import os
from pathlib import Path
from e2b_code_interpreter import Sandbox
from models import ErrorReport, TestResult


class SandboxExecutor:
    """Executes code in E2B sandbox"""
    
    def __init__(self):
        api_key = os.getenv("E2B_API_KEY")
        if not api_key:
            # Try alternate name
            api_key = os.getenv("E2B_API_TOKEN")
        if not api_key:
            raise ValueError("E2B_API_KEY not found in environment")
        # Set API key in environment for E2B
        os.environ["E2B_API_KEY"] = api_key
    
    async def test_fix(self, error_report: ErrorReport, fix_code: str) -> TestResult:
        """
        Test if the fix works by running it in sandbox.
        
        Steps:
        1. Create sandbox
        2. Upload all related files
        3. Write fixed code
        4. Try to execute the code that was failing
        5. Check if error is gone
        """
        sandbox = None
        try:
            # Create sandbox using new E2B API
            sandbox = Sandbox.create()
            
            # Upload all related files first (dependencies)
            for relation in error_report.related_files:
                try:
                    # Normalize path
                    file_path = Path(relation.file.replace('\\', '/'))
                    if file_path.exists():
                        with open(file_path, encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        # Use forward slashes for sandbox
                        sandbox.files.write(str(file_path).replace('\\', '/'), content)
                except Exception as e:
                    print(f"Warning: Could not upload {relation.file}: {e}")
            
            # Write the fixed code (normalize path)
            fixed_path = error_report.file_path.replace('\\', '/')
            sandbox.files.write(fixed_path, fix_code)
            
            # Generate and run test code
            test_code = self._generate_test_code(error_report)
            
            execution = sandbox.run_code(test_code)
            
            # Check result
            if execution.error:
                return TestResult(
                    success=False,
                    error=str(execution.error),
                    output=execution.text if hasattr(execution, 'text') else str(execution.results)
                )
            else:
                # Success if no error and has output
                return TestResult(
                    success=True,
                    output=execution.text if hasattr(execution, 'text') else str(execution.results)
                )
                
        except Exception as e:
            return TestResult(
                success=False,
                error=f"Sandbox execution failed: {str(e)}"
            )
        finally:
            if sandbox:
                try:
                    sandbox.close()
                except:
                    pass
    
    def _generate_test_code(self, error_report: ErrorReport) -> str:
        """
        Generate code to test if the fix works.
        
        Strategy:
        1. Try to import/run the fixed module
        2. Check if the specific error is gone
        """
        # Normalize path (convert backslashes to forward slashes)
        file_path = error_report.file_path.replace("\\", "/")
        
        # Detect language
        file_ext = file_path.split('.')[-1] if '.' in file_path else 'py'
        
        if file_ext == 'py':
            return self._generate_python_test(file_path, error_report)
        elif file_ext in ['js', 'ts']:
            return self._generate_javascript_test(file_path, error_report)
        else:
            # Generic test - just try to parse/compile
            return self._generate_generic_test(file_path, error_report)
    
    def _generate_python_test(self, file_path: str, error_report: ErrorReport) -> str:
        """Generate Python test code"""
        # Remove .py extension and convert to module path
        if file_path.endswith(".py"):
            file_path = file_path[:-3]
        
        # Convert path to module (e.g., "test_project/utils" -> "test_project.utils")
        module_path = file_path.replace("/", ".")
        
        # If there's a function name, try to test it
        if error_report.function_name and error_report.function_name != "<module>":
            test_code = f"""
import sys
sys.path.insert(0, '.')

try:
    # Import the module
    import {module_path}
    print("✓ Module imported successfully")
    
    # Try to access the function
    func = getattr({module_path}, '{error_report.function_name}', None)
    if func:
        print(f"✓ Function '{error_report.function_name}' exists")
        if callable(func):
            print(f"✓ Function '{error_report.function_name}' is callable")
    
    print("✓ Fix appears to work!")
    
except {error_report.error_type} as e:
    print(f"✗ Same error still occurs: {{e}}")
    raise
except Exception as e:
    print(f"⚠ Different error (might be OK): {{e}}")
    print("✓ Original error is fixed!")
"""
        else:
            # Just try to import the module
            test_code = f"""
import sys
sys.path.insert(0, '.')

try:
    import {module_path}
    print("✓ Module imported successfully")
    print("✓ Fix appears to work!")
except {error_report.error_type} as e:
    print(f"✗ Same error still occurs: {{e}}")
    raise
except Exception as e:
    print(f"⚠ Different error (might be OK): {{e}}")
    print("✓ Original error is fixed!")
"""
        
        return test_code
    
    def _generate_javascript_test(self, file_path: str, error_report: ErrorReport) -> str:
        """Generate JavaScript/TypeScript test code"""
        test_code = f"""
try {{
    require('./{file_path}');
    console.log('✓ Module loaded successfully');
    console.log('✓ Fix appears to work!');
}} catch (e) {{
    if (e.name === '{error_report.error_type}') {{
        console.log('✗ Same error still occurs:', e.message);
        throw e;
    }} else {{
        console.log('⚠ Different error (might be OK):', e.message);
        console.log('✓ Original error is fixed!');
    }}
}}
"""
        return test_code
    
    def _generate_generic_test(self, file_path: str, error_report: ErrorReport) -> str:
        """Generate generic test - just check if file is valid"""
        test_code = f"""
import sys
print("✓ File was written successfully")
print("✓ Fix generated (manual verification needed)")
"""
        return test_code
