"""
Claude API Runner with Slovak Language Support
Handles all communication with Claude API.
"""

import os
import sys
import io
from pathlib import Path
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

# Force UTF-8 output for Windows console
if sys.platform == 'win32':
    # Set console to UTF-8 mode
    os.system('chcp 65001 > nul')
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer,
        encoding='utf-8',
        errors='replace'
    )


def sanitize_for_console(text: str) -> str:
    """
    Remove emoji and Unicode chars for safe Windows console output.
    Used only for printing to console, not for file output.
    """
    replacements = {
        '✅': '[OK]',
        '❌': '[ERROR]',
        '📊': '[INFO]',
        '🚀': '[START]',
        '⚠️': '[WARNING]',
        '💬': '[RESPONSE]',
        '🎯': '[GOAL]',
        '📝': '[NOTE]',
        '🔍': '[SEARCH]',
        '💡': '[TIP]',
        '🔧': '[FIX]',
        '🐛': '[BUG]',
        '🎉': '[SUCCESS]',
        '📈': '[STATS]',
        '💰': '[COST]',
    }

    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)

    return text


class ClaudeRunner:
    """Handles Claude API interactions with Slovak language enforcement."""

    def __init__(self, model: str = "claude-sonnet-4-5-20250929", max_tokens: int = 8000):
        """
        Initialize Claude API client.

        Args:
            model: Claude model to use
            max_tokens: Maximum tokens for response
        """
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens

    def create_slovak_system_prompt(self) -> str:
        """
        Create system prompt that enforces Slovak language responses.

        Returns:
            System prompt string
        """
        return """You are an expert AI assistant specialized in software development and code analysis.

CRITICAL: ALWAYS respond in Slovak language. Your entire response must be in Slovak.

Your capabilities:
- Analyze code and project structure
- Suggest improvements and next steps
- Create, modify, and delete files when needed
- Provide detailed technical explanations in Slovak

When working with files, use this XML format:

<file_operations>
  <operation type="create|modify|delete" path="relative/path/to/file">
    <content>
    File content here (for create/modify)
    </content>
  </operation>
</file_operations>

Important:
- Always respond in Slovak language
- Be specific and actionable
- Consider project context from session notes
- Suggest concrete next steps
- If you modify files, provide complete content, not snippets
"""

    def send_task(
        self,
        task_description: str,
        context: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send task to Claude with Slovak language enforcement.

        Args:
            task_description: Main task description
            context: Additional context (smart context)
            notes: Additional notes or requirements

        Returns:
            Dict with response and metadata:
            {
                'response': str,
                'usage': {
                    'input_tokens': int,
                    'output_tokens': int,
                    'total_tokens': int
                },
                'stop_reason': str
            }
        """
        # Build user message
        user_message = f"# Úloha\n\n{task_description}\n\n"

        if context:
            user_message += f"# Kontext\n\n{context}\n\n"

        if notes:
            user_message += f"# Poznámky\n\n{notes}\n\n"

        # Add reminder to respond in Slovak
        user_message += "\n**Odpoveď v slovenčine.**"

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=self.create_slovak_system_prompt(),
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            # Extract response
            response_text = ""
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            # Return result
            return {
                'response': response_text,
                'usage': {
                    'input_tokens': message.usage.input_tokens,
                    'output_tokens': message.usage.output_tokens,
                    'total_tokens': message.usage.input_tokens + message.usage.output_tokens
                },
                'stop_reason': message.stop_reason
            }

        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")


# Test section
if __name__ == "__main__":
    from dotenv import load_dotenv

    # Load .env file from workspace directory
    env_path = Path(__file__).parent.parent / 'workspace' / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[INFO] Loaded .env from: {env_path}")

    print("\n[TEST] Testing ClaudeRunner...")

    try:
        # Initialize runner
        api_key = os.getenv('ANTHROPIC_API_KEY')
        print(f"[OK] API key found: {api_key[:12]}...{api_key[-4:]}")

        runner = ClaudeRunner()
        print(f"[OK] ClaudeRunner initialized")
        print(f"     Model: {runner.model}")

        # Send test task
        print(f"\n[INFO] Sending test task to Claude...")
        result = runner.send_task(
            task_description="Analyzuj tento testovací task a povedz mi či funguje Slovak language enforcement.",
            notes="Toto je len test. Odpoveď v slovenčine prosím."
        )

        print(f"[OK] API call successful!")
        print(f"     Input tokens: {result['usage']['input_tokens']}")
        print(f"     Output tokens: {result['usage']['output_tokens']}")
        print(f"     Total tokens: {result['usage']['total_tokens']}")
        print(f"     Stop reason: {result['stop_reason']}")

        print(f"\n[RESPONSE] Claude's response:")
        print("-" * 60)

        # Sanitize response for console output (remove emoji only)
        safe_response = sanitize_for_console(result['response'])
        print(safe_response)

        print("-" * 60)
        print("\n[SUCCESS] Test completed successfully!")

    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        sys.exit(1)