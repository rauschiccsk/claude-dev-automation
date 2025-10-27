"""
claude_runner.py - Claude API interaction handler
Handles API calls to Claude with proper error handling and token tracking
"""

import os
from typing import Dict, Any, Optional
from anthropic import Anthropic


class ClaudeRunner:
    """Handles communication with Claude API."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude API client.

        Args:
            api_key: Anthropic API key (if None, reads from environment)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')

        if not self.api_key:
            raise ValueError(
                "API key not provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5

    def execute(
        self,
        task: str,
        context: str,
        max_tokens: int = 8000,
        temperature: float = 1.0
    ) -> Dict[str, Any]:
        """
        Execute task with Claude.

        Args:
            task: Task description
            context: Full context including smart context
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature (0.0-1.0)

        Returns:
            Dict with 'response' and 'usage' keys
        """
        try:
            # Build messages
            messages = [
                {
                    "role": "user",
                    "content": self._build_prompt(task, context)
                }
            ]

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )

            # Extract response text
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            # Build result
            result = {
                'response': response_text,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                },
                'model': response.model,
                'stop_reason': response.stop_reason
            }

            return result

        except Exception as e:
            raise RuntimeError(f"Claude API call failed: {str(e)}")

    def _build_prompt(self, task: str, context: str) -> str:
        """
        Build complete prompt for Claude.

        Args:
            task: Task description
            context: Smart context with project info

        Returns:
            Complete prompt string
        """
        prompt = f"""{context}

---

## 🎯 YOUR TASK

{task}

## 📋 INSTRUCTIONS

Analyze the task and context above. Then:

1. **If the task requires code changes:**
   - Provide clear file operation instructions
   - Use format: FILE_OPERATION: CREATE/MODIFY/DELETE
   - Include full file paths relative to project root
   - Provide complete file content for CREATE/MODIFY operations

2. **If the task is analysis/recommendations only:**
   - Provide thorough analysis
   - Give actionable recommendations
   - Structure your response clearly
   - No file operations needed

3. **Always:**
   - Respond in Slovak language (CRITICAL)
   - Be specific and actionable
   - Explain your reasoning
   - Consider project context

## 📝 FILE OPERATION FORMAT

When you need to modify files, use this format:

```
FILE_OPERATION: MODIFY
PATH: src/example.py
CONTENT:
```python
# Complete file content here
def example():
    pass
```
```

FILE_OPERATION: CREATE
PATH: tests/test_new.py
CONTENT:
```python
# Complete new file content
import pytest
```
```

Remember: ALWAYS respond in Slovak language!
"""

        return prompt


# Example usage and testing
if __name__ == "__main__":
    import sys
    from pathlib import Path
    from dotenv import load_dotenv

    # Load .env file from workspace directory for standalone testing
    env_path = Path(__file__).parent.parent / 'workspace' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[INFO] Loaded .env from: {env_path}")
    else:
        print(f"[WARNING] .env not found at: {env_path}")

    print("[TEST] Testing ClaudeRunner...")

    # Check API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set in environment")
        print("        Set it in workspace/.env or system environment")
        sys.exit(1)

    print(f"[OK] API key found: {api_key[:10]}...{api_key[-4:]}")

    # Initialize runner
    try:
        runner = ClaudeRunner(api_key)
        print(f"[OK] ClaudeRunner initialized")
        print(f"     Model: {runner.model}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}")
        sys.exit(1)

    # Test simple task
    print("\n[INFO] Sending test task to Claude...")

    test_context = """
# Project: claude-dev-automation
# Description: Testing ClaudeRunner

## Project Status
System is operational and testing API connectivity.
"""

    test_task = "Povedz mi že si úspešne prijal túto správu a že všetko funguje."

    try:
        result = runner.execute(
            task=test_task,
            context=test_context,
            max_tokens=500
        )

        print(f"\n[OK] API call successful!")
        print(f"     Input tokens: {result['usage']['input_tokens']:,}")
        print(f"     Output tokens: {result['usage']['output_tokens']:,}")
        print(f"     Total tokens: {result['usage']['total_tokens']:,}")
        print(f"     Stop reason: {result['stop_reason']}")

        print(f"\n[RESPONSE] Claude's response:")
        print("-" * 60)
        print(result['response'])
        print("-" * 60)

    except Exception as e:
        print(f"\n[ERROR] API call failed: {e}")
        sys.exit(1)

    print("\n[OK] All tests passed!")