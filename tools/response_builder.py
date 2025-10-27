"""
response_builder.py - Builds formatted markdown responses
Generates response.md with Claude's analysis and file changes
"""

from typing import List, Dict, Optional
from datetime import datetime


class ResponseBuilder:
    """Builds formatted markdown response files."""

    def build_response(
        self,
        task: str,
        priority: str,
        file_changes: List[Dict],
        token_usage: Optional[Dict] = None,
        timestamp: Optional[str] = None,
        git_status: Optional[str] = None,
        claude_response: Optional[str] = None,  # ← ADDED: Claude's analysis text
    ) -> str:
        """
        Build formatted response markdown.

        Args:
            task: Task description
            priority: Task priority (LOW/NORMAL/HIGH)
            file_changes: List of file operation results
            token_usage: Token usage statistics
            timestamp: ISO timestamp
            git_status: Git status output
            claude_response: Claude's analysis text (when no files changed)

        Returns:
            Formatted markdown string
        """
        response = "# 🤖 Claude Development Response\n\n"

        # Header with metadata
        response += self._build_header(task, priority, timestamp)

        # Token usage
        if token_usage:
            response += self._build_token_usage(token_usage)

        # Claude's Analysis (when no file changes)
        if claude_response:
            response += self._build_claude_analysis(claude_response)

        # Git status (if available)
        if git_status:
            response += self._build_git_status(git_status)

        # File changes (if any)
        if file_changes:
            response += self._build_file_changes(file_changes)
        else:
            if not claude_response:
                response += "## 📝 File Changes\n\n"
                response += "_No file changes were made._\n\n"

        # Footer
        response += self._build_footer()

        return response

    def _build_header(self, task: str, priority: str, timestamp: Optional[str]) -> str:
        """Build response header."""
        header = f"**Timestamp:** {timestamp or datetime.now().isoformat()}\n"
        header += f"**Priority:** {priority}\n\n"
        header += "---\n\n"
        header += "## 🎯 Task\n\n"
        header += f"{task}\n\n"
        return header

    def _build_token_usage(self, usage: Dict) -> str:
        """Build token usage section."""
        section = "## 💰 Token Usage\n\n"
        section += f"- **Input tokens:** {usage.get('input_tokens', 0):,}\n"
        section += f"- **Output tokens:** {usage.get('output_tokens', 0):,}\n"
        section += f"- **Total tokens:** {usage.get('total_tokens', 0):,}\n"

        # Calculate cost estimate (Claude Sonnet 4.5 pricing)
        input_cost = usage.get('input_tokens', 0) * 0.003 / 1000
        output_cost = usage.get('output_tokens', 0) * 0.015 / 1000
        total_cost = input_cost + output_cost

        section += f"- **Estimated cost:** ${total_cost:.4f}\n\n"
        return section

    def _build_claude_analysis(self, analysis: str) -> str:
        """
        Build Claude's analysis section.
        This is shown when Claude provides recommendations without file changes.
        """
        section = "## 💬 Claude's Analysis\n\n"
        section += analysis.strip() + "\n\n"
        section += "---\n\n"
        return section

    def _build_git_status(self, status: str) -> str:
        """Build Git status section."""
        section = "## 📊 Git Status\n\n"
        section += "```\n"
        section += status.strip()
        section += "\n```\n\n"
        return section

    def _build_file_changes(self, changes: List[Dict]) -> str:
        """Build file changes section."""
        section = "## 📝 File Changes\n\n"
        section += f"**Total files modified:** {len(changes)}\n\n"

        for i, change in enumerate(changes, 1):
            section += f"### {i}. {change['path']}\n\n"
            section += f"**Operation:** `{change['operation']}`\n"

            if change.get('success'):
                section += f"**Status:** ✅ Success\n"
            else:
                section += f"**Status:** ❌ Failed\n"
                if change.get('error'):
                    section += f"**Error:** {change['error']}\n"

            # Show file preview for small files
            if change.get('content') and len(change['content']) < 2000:
                section += f"\n**Preview:**\n```{self._detect_language(change['path'])}\n"
                section += change['content'][:500]
                if len(change['content']) > 500:
                    section += "\n... (truncated)"
                section += "\n```\n"
            elif change.get('content'):
                lines = change['content'].count('\n') + 1
                chars = len(change['content'])
                section += f"\n**Size:** {lines} lines, {chars:,} characters\n"

            section += "\n"

        return section

    def _detect_language(self, path: str) -> str:
        """Detect code language from file extension."""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'jsx',
            '.tsx': 'tsx',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.sql': 'sql',
            '.sh': 'bash',
            '.ps1': 'powershell',
        }

        for ext, lang in ext_map.items():
            if path.endswith(ext):
                return lang

        return ''

    def _build_footer(self) -> str:
        """Build response footer."""
        footer = "---\n\n"
        footer += "_Generated by Claude Dev Automation_\n"
        footer += f"_Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n"
        return footer


if __name__ == "__main__":
    builder = ResponseBuilder()

    # Example 1: Response with file changes
    response1 = builder.build_response(
        task="Add logging to authentication module",
        priority="HIGH",
        file_changes=[
            {
                'path': 'src/auth.py',
                'operation': 'MODIFY',
                'success': True,
                'content': 'import logging\n\nlogger = logging.getLogger(__name__)\n'
            }
        ],
        token_usage={
            'input_tokens': 1500,
            'output_tokens': 800,
            'total_tokens': 2300
        }
    )

    print("Example 1: With file changes")
    print("="*60)
    print(response1)
    print("\n\n")

    # Example 2: Response with analysis only (no file changes)
    response2 = builder.build_response(
        task="Analyzuj projekt a navrhni vylepšenia",
        priority="NORMAL",
        file_changes=[],
        claude_response="""
Analyzoval som projekt a identifikoval som nasledujúce oblasti na vylepšenie:

## 🔍 Zistenia

1. **Testovanie**
   - Pokrytie testami je 65%, odporúčam zvýšiť na 80%+
   - Chýbajú integračné testy pre API endpointy

2. **Dokumentácia**
   - README.md je zastaraný
   - Chýba API dokumentácia

3. **Výkon**
   - Databázové queries nie sú optimalizované
   - Odporúčam pridať indexy na `user_id` a `created_at`

## 💡 Odporúčania

1. Začať s testovaním - najväčší impact
2. Aktualizovať dokumentáciu
3. Optimalizovať databázu v ďalšej fáze
        """,
        token_usage={
            'input_tokens': 4200,
            'output_tokens': 850,
            'total_tokens': 5050
        }
    )

    print("Example 2: Analysis only (no file changes)")
    print("="*60)
    print(response2)