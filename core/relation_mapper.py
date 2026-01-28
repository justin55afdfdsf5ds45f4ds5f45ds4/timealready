"""
Relation Mapper - Maps file dependencies from stack trace
Pure logic, no LLM needed.
"""
from pathlib import Path
from typing import List
from models import StackFrame, FileRelation


class RelationMapper:
    """Maps file relations from stack trace"""
    
    def __init__(self, codebase_path: Path):
        self.codebase_path = codebase_path
    
    def map_from_stacktrace(self, stack_trace: List[StackFrame]) -> List[FileRelation]:
        """
        Extract file relations from stack trace.
        
        Stack trace shows EXACT call chain:
        File A calls File B calls File C (where error happened)
        
        So relations are:
        A → B (A depends on B)
        B → C (B depends on C)
        """
        relations = []
        
        for i in range(len(stack_trace) - 1):
            caller = stack_trace[i]
            callee = stack_trace[i + 1]
            
            relations.append(FileRelation(
                file=caller.file,
                line=caller.line,
                depends_on=callee.file,
                depends_on_line=callee.line,
                relationship_type="calls"
            ))
        
        return relations
