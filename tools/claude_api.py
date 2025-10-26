#!/usr/bin/env python3
"""
Claude API Client
Wrapper for Anthropic Claude API with token tracking and error handling
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from anthropic import Anthropic
from config_manager import get_config

class ClaudeAPIClient:
    """Claude API client with automatic token tracking"""
    
    def __init__(self):
        """Initialize Claude API client"""
        self.config = get_config()
        self.client = Anthropic(api_key=self.config.anthropic_api_key)
        self.workspace_root = Path(self.config.workspace_root)
        self.logs_dir = self.workspace_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
    def analyze(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send prompt to Claude and get response
        
        Args:
            prompt: User prompt
            system_prompt: System instructions (optional)
            max_tokens: Max tokens in response
            temperature: Sampling temperature
            metadata: Additional metadata for logging
            
        Returns:
            Dict with response text, tokens used, and metadata
        """
        
        # Use defaults from config
        max_tokens = max_tokens or self.config.claude_max_tokens
        temperature = temperature or self.config.claude_temperature
        
        # Build messages
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Call API
        try:
            start_time = datetime.now()
            
            response = self.client.messages.create(
                model=self.config.claude_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "",
                messages=messages
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Extract response
            response_text = response.content[0].text
            
            # Token usage
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            total_tokens = input_tokens + output_tokens
            
            # Build result
            result = {
                "success": True,
                "response": response_text,
                "tokens": {
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": total_tokens
                },
                "model": self.config.claude_model,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log usage
            self._log_usage(
                prompt=prompt[:200],  # First 200 chars
                response=response_text[:200],
                tokens=result["tokens"],
                duration=duration,
                metadata=metadata
            )
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.now().isoformat()
            }
            
            # Log error
            self._log_error(error_result, metadata)
            
            return error_result
    
    def _log_usage(
        self,
        prompt: str,
        response: str,
        tokens: Dict[str, int],
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log API usage to JSONL file"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "prompt_preview": prompt,
            "response_preview": response,
            "tokens": tokens,
            "duration_seconds": duration,
            "model": self.config.claude_model,
            "metadata": metadata or {}
        }
        
        # Append to daily log file
        log_file = self.logs_dir / f"api_usage_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def _log_error(
        self,
        error_result: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log API errors"""
        
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error": error_result.get("error"),
            "error_type": error_result.get("error_type"),
            "metadata": metadata or {}
        }
        
        # Append to error log
        error_file = self.logs_dir / "api_errors.jsonl"
        
        with open(error_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_entry, ensure_ascii=False) + '\n')
    
    def get_daily_usage(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Get token usage statistics for a specific day
        
        Args:
            date: Date to check (default: today)
            
        Returns:
            Dict with usage statistics
        """
        
        date = date or datetime.now()
        log_file = self.logs_dir / f"api_usage_{date.strftime('%Y%m%d')}.jsonl"
        
        if not log_file.exists():
            return {
                "date": date.strftime('%Y-%m-%d'),
                "total_calls": 0,
                "total_tokens": 0,
                "input_tokens": 0,
                "output_tokens": 0
            }
        
        total_calls = 0
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                total_calls += 1
                tokens = entry.get('tokens', {})
                total_tokens += tokens.get('total', 0)
                input_tokens += tokens.get('input', 0)
                output_tokens += tokens.get('output', 0)
        
        return {
            "date": date.strftime('%Y-%m-%d'),
            "total_calls": total_calls,
            "total_tokens": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": self._estimate_cost(input_tokens, output_tokens)
        }
    
    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate API cost based on Claude Sonnet 4.5 pricing
        
        Pricing (as of Oct 2025):
        - Input: $3 per million tokens
        - Output: $15 per million tokens
        """
        
        input_cost = (input_tokens / 1_000_000) * 3.0
        output_cost = (output_tokens / 1_000_000) * 15.0
        
        return round(input_cost + output_cost, 4)


# Singleton instance
_client_instance = None

def get_claude_client() -> ClaudeAPIClient:
    """Get singleton Claude API client"""
    global _client_instance
    if _client_instance is None:
        _client_instance = ClaudeAPIClient()
    return _client_instance


if __name__ == "__main__":
    # Test Claude API
    print("Testing Claude API Client...")
    print("=" * 60)
    
    try:
        client = ClaudeAPIClient()
        
        # Simple test
        result = client.analyze(
            prompt="Povedz 'Hello from automation system!' v slovenčine.",
            metadata={"test": True, "purpose": "connection_test"}
        )
        
        if result["success"]:
            print("✅ API Connection successful!")
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"✅ Tokens used: {result['tokens']['total']}")
            print(f"✅ Duration: {result['duration_seconds']:.2f}s")
            
            # Check daily usage
            usage = client.get_daily_usage()
            print(f"\n📊 Today's usage:")
            print(f"   Calls: {usage['total_calls']}")
            print(f"   Tokens: {usage['total_tokens']:,}")
            print(f"   Estimated cost: ${usage['estimated_cost_usd']:.4f}")
        else:
            print(f"❌ API Error: {result['error']}")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")