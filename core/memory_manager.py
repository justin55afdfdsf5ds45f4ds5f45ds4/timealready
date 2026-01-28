"""
Memory Manager - Stores and retrieves fixes using UltraContext
"""
import os
import hashlib
from typing import List
from models import ErrorReport, FixResult, LearnedFix
from datetime import datetime


class MemoryManager:
    """Manages learned fixes in UltraContext"""
    
    def __init__(self):
        self.api_key = os.getenv("ULTRACONTEXT_API_KEY")
        # TODO: Initialize UltraContext client when SDK available
        # For now, use local storage
        self.local_storage = {}
    
    async def retrieve_similar(self, error_report: ErrorReport) -> List[LearnedFix]:
        """
        Retrieve similar fixes from memory.
        
        Matches by:
        1. Error type (exact)
        2. File pattern (similar paths)
        3. Success rate (prefer fixes that worked)
        """
        signature = self._generate_signature(error_report)
        
        # TODO: Use UltraContext API
        # For now, simple local lookup
        matches = []
        for key, fix in self.local_storage.items():
            if fix.error_type == error_report.error_type:
                matches.append(fix)
        
        # Sort by success rate
        matches.sort(key=lambda f: f.success_rate, reverse=True)
        
        return matches[:5]  # Top 5
    
    async def store_fix(self, error_report: ErrorReport, fix_result: FixResult):
        """Store successful fix in memory"""
        signature = self._generate_signature(error_report)
        
        learned_fix = LearnedFix(
            error_signature=signature,
            error_type=error_report.error_type,
            file_pattern=self._extract_pattern(error_report.file_path),
            fix_strategy=fix_result.fix_strategy or "Applied code fix",
            success_count=1,
            created_at=datetime.utcnow()
        )
        
        # TODO: Store in UltraContext
        # For now, local storage
        self.local_storage[signature] = learned_fix
        
        print(f"💾 Stored fix: {signature[:16]}...")
    
    def _generate_signature(self, error_report: ErrorReport) -> str:
        """Generate unique signature for error"""
        # Combine error type + file pattern + line context
        context = f"{error_report.error_type}:{error_report.file_path}:{error_report.error_message}"
        return hashlib.md5(context.encode()).hexdigest()
    
    def _extract_pattern(self, file_path: str) -> str:
        """Extract file pattern (e.g., 'api/*.py')"""
        parts = file_path.split('/')
        if len(parts) > 1:
            return f"{parts[0]}/*.py"
        return "*.py"
