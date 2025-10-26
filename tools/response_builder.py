#!/usr/bin/env python3
"""
Response Builder
Formats responses for response.md file
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

class ResponseBuilder:
    """Build formatted responses for response.md"""
    
    def __init__(self):
        """Initialize response builder"""
        self.sections = []
        
    def build_response(
        self,
        project_name: str,
        task_summary: str,
        status: str,
        tokens_used: Dict[str, int],
        file_changes: List[Dict[str, Any]] = None,
        git_result: Dict[str, Any] = None,
        test_results: Optional[str] = None,
        notes: Optional[str] = None,
        next_steps: Optional[List[str]] = None
    ) -> str:
        """
        Build complete response
        
        Args:
            project_name: Project name
            task_summary: Brief task summary
            status: Status (✅ COMPLETED, ⏳ IN PROGRESS, ❌ FAILED)
            tokens_used: Dict with input/output/total tokens
            file_changes: List of file change results
            git_result: Git commit/push results
            test_results: Test output
            notes: Additional notes
            next_steps: List of next steps
            
        Returns:
            Formatted markdown response
        """
        
        # Header
        response = f"""# Task Response
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project:** {project_name}  
**Status:** {status}  
**Tokens used:** {tokens_used.get('total', 0):,} (saved {40000 - tokens_used.get('total', 0):,} vs chat init)

---

## Summary
{task_summary}

"""
        
        # File changes section
        if file_changes:
            response += "## Changes Made\n\n"
            
            successful = [c for c in file_changes if c.get('success', False)]
            failed = [c for c in file_changes if not c.get('success', False)]
            
            if successful:
                response += f"### 📝 Modified Files ({len(successful)})\n\n"
                for change in successful:
                    file_path = change.get('file', 'unknown')
                    action = change.get('action', 'modified')
                    response += f"{self._get_change_icon(action)} **{file_path}** - {action}\n"
                response += "\n"
            
            if failed:
                response += f"### ❌ Failed Operations ({len(failed)})\n\n"
                for change in failed:
                    file_path = change.get('file', 'unknown')
                    error = change.get('error', 'Unknown error')
                    response += f"- **{file_path}**: {error}\n"
                response += "\n"
        
        # Git operations section
        if git_result:
            response += "## Git Operations\n\n"
            
            commit = git_result.get('commit')
            push = git_result.get('push')
            
            if commit:
                if commit.get('success'):
                    hash = commit.get('commit_hash', 'unknown')
                    msg = commit.get('message', '')
                    response += f"- ✅ Commit: `{hash}` - {msg}\n"
                else:
                    error = commit.get('error', 'Unknown error')
                    response += f"- ❌ Commit failed: {error}\n"
            
            if push:
                if push.get('success'):
                    remote = push.get('remote', 'origin')
                    response += f"- ✅ Pushed to: {remote}\n"
                else:
                    response += f"- ⏸️  Push: NOT executed (AUTO_PUSH: no)\n"
            elif git_result.get('commit', {}).get('success'):
                response += "- ⏸️  Push: NOT executed (AUTO_PUSH: no)\n"
            
            response += "\n"
        
        # Test results section
        if test_results:
            response += "## Test Results\n\n"
            response += "```\n"
            response += test_results
            response += "\n```\n\n"
        
        # Notes section
        if notes:
            response += "## Notes\n\n"
            response += notes + "\n\n"
        
        # Next steps section
        if next_steps:
            response += "## Next Steps\n\n"
            for i, step in enumerate(next_steps, 1):
                response += f"{i}. {step}\n"
            response += "\n"
        
        # Token usage details
        response += "## Token Usage\n\n"
        response += "| Category | Tokens |\n"
        response += "|----------|--------|\n"
        response += f"| Context  | {tokens_used.get('input', 0):,} |\n"
        response += f"| Response | {tokens_used.get('output', 0):,} |\n"
        response += f"| **Total**| **{tokens_used.get('total', 0):,}** |\n"
        response += "\n"
        
        # Cost estimate
        cost = self._estimate_cost(
            tokens_used.get('input', 0),
            tokens_used.get('output', 0)
        )
        response += f"**Estimated cost:** ${cost:.4f}\n\n"
        
        # Footer
        response += "---\n"
        response += "*All changes have been written to your project directory.*\n"
        response += "*Review git diff in PyCharm before pushing.*\n"
        
        return response
    
    def _get_change_icon(self, action: str) -> str:
        """Get emoji icon for change type"""
        icons = {
            "created": "✨",
            "updated": "📝",
            "deleted": "🗑️",
            "overwritten": "♻️"
        }
        return icons.get(action, "📄")
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate API cost"""
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        return input_cost + output_cost
    
    def build_error_response(
        self,
        project_name: str,
        error_message: str,
        error_details: Optional[str] = None
    ) -> str:
        """Build error response"""
        
        response = f"""# Task Response
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project:** {project_name}  
**Status:** ❌ ERROR

---

## Error

{error_message}

"""
        
        if error_details:
            response += "### Details\n\n"
            response += "```\n"
            response += error_details
            response += "\n```\n\n"
        
        response += "---\n"
        response += "*Please check the error and try again.*\n"
        
        return response


if __name__ == "__main__":
    # Test response builder
    print("Testing Response Builder...")
    print("=" * 60)
    
    try:
        builder = ResponseBuilder()
        
        # Test successful response
        print("\n1. Building success response...")
        
        response = builder.build_response(
            project_name="uae-legal-agent",
            task_summary="Added retry mechanism with exponential backoff",
            status="✅ COMPLETED",
            tokens_used={
                "input": 1234,
                "output": 2345,
                "total": 3579
            },
            file_changes=[
                {
                    "success": True,
                    "action": "created",
                    "file": "src/core/retry.py"
                },
                {
                    "success": True,
                    "action": "updated",
                    "file": "tests/test_retry.py"
                }
            ],
            git_result={
                "commit": {
                    "success": True,
                    "commit_hash": "abc123f",
                    "message": "Add retry mechanism"
                },
                "push": None
            },
            test_results="All tests passed (2/2)",
            next_steps=[
                "Review git diff in PyCharm",
                "Test with real API",
                "Push to repository"
            ]
        )
        
        print("✅ Success response built")
        print(f"   Length: {len(response)} chars")
        
        # Test error response
        print("\n2. Building error response...")
        
        error_response = builder.build_error_response(
            project_name="test-project",
            error_message="API key not found",
            error_details="ANTHROPIC_API_KEY not set in .env file"
        )
        
        print("✅ Error response built")
        print(f"   Length: {len(error_response)} chars")
        
        print("\n" + "=" * 60)
        print("✅ Response Builder test passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")