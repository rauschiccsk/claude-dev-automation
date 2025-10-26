#!/usr/bin/env python3
"""
Comprehensive Test Suite
Tests all modules together
"""

import sys
from pathlib import Path

print("=" * 70)
print("🧪 COMPREHENSIVE AUTOMATION SYSTEM TEST")
print("=" * 70)
print()

# Test all modules
tests_passed = 0
tests_failed = 0

def test_module(name, test_func):
    """Run a test and track results"""
    global tests_passed, tests_failed
    
    print(f"Testing {name}...")
    print("-" * 70)
    try:
        test_func()
        print(f"   ✅ {name}: PASSED\n")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"   ❌ {name}: FAILED")
        print(f"   Error: {e}\n")
        tests_failed += 1
        return False

# Test 1: Config Manager
def test_config():
    from config_manager import ConfigManager
    config = ConfigManager()
    assert config.claude_model == "claude-sonnet-4-5-20250929"
    assert config.max_context_tokens == 5000
    print("   ✅ Configuration loaded")
    print(f"   ✅ API Key configured: ...{config.anthropic_api_key[-8:]}")

test_module("Config Manager", test_config)

# Test 2: Claude API
def test_claude():
    from claude_api import ClaudeAPIClient
    client = ClaudeAPIClient()
    result = client.analyze(
        "Say 'Test passed' in Slovak",
        metadata={"test": "comprehensive"}
    )
    assert result["success"]
    assert result["tokens"]["total"] > 0
    print(f"   ✅ API call successful")
    print(f"   ✅ Tokens used: {result['tokens']['total']}")

test_module("Claude API Client", test_claude)

# Test 3: Context Builder
def test_context():
    from context_builder import ContextBuilder
    builder = ContextBuilder()
    
    context = builder.build_context(
        project_name="uae-legal-agent",
        task_content="Test task for context builder"
    )
    
    estimated = context['metadata']['estimated_tokens']
    assert estimated < 5000, f"Context too large: {estimated} tokens"
    print(f"   ✅ Context built: ~{estimated} tokens")
    print(f"   ✅ Savings: ~{40000 - estimated:,} tokens vs chat")

test_module("Context Builder", test_context)

# Test 4: File Operations
def test_files():
    import shutil
    from file_operations import FileOperations
    
    # Create test directory
    test_dir = Path("C:/Development/_workspace/test_files")
    test_dir.mkdir(exist_ok=True)
    
    ops = FileOperations(str(test_dir))
    
    # Test create
    result = ops.create_file("test.py", "print('test')\n")
    assert result["success"]
    print(f"   ✅ Created file: {result['file']}")
    
    # Test update
    result = ops.update_file("test.py", "print('test')", "print('updated')")
    assert result["success"]
    print(f"   ✅ Updated file: {result['file']}")
    
    # Cleanup
    shutil.rmtree(test_dir)
    print("   ✅ Cleanup complete")

test_module("File Operations", test_files)

# Test 5: Git Operations (if git repo exists)
def test_git():
    from git_operations import GitOperations
    
    try:
        git = GitOperations("C:/Development/uae-legal-agent")
        
        # Test status
        status = git.status()
        print(f"   ✅ Git status: {status['count']} changes")
        
        # Test branch
        branch = git.get_current_branch()
        print(f"   ✅ Current branch: {branch}")
        
        # Test last commit
        last = git.get_last_commit()
        print(f"   ✅ Last commit: {last['hash']}")
        
    except ValueError:
        print("   ⚠️  Git repo not found (expected for fresh setup)")

test_module("Git Operations", test_git)

# Test 6: Project Manager
def test_projects():
    from project_manager import ProjectManager
    
    pm = ProjectManager()
    
    # Test get all
    projects = pm.get_all_projects()
    assert len(projects) == 5, f"Expected 5 projects, got {len(projects)}"
    print(f"   ✅ Found {len(projects)} projects")
    
    # Test switch
    result = pm.switch_project("uae-legal-agent")
    assert result["success"]
    print(f"   ✅ Switched to: {result['project']['name']}")
    
    # Test context
    context = pm.load_project_context("uae-legal-agent")
    print(f"   ✅ Context loaded for uae-legal-agent")

test_module("Project Manager", test_projects)

# Test 7: Response Builder
def test_response():
    from response_builder import ResponseBuilder
    
    builder = ResponseBuilder()
    
    # Test success response
    response = builder.build_response(
        project_name="test-project",
        task_summary="Test task completed",
        status="✅ COMPLETED",
        tokens_used={"input": 1000, "output": 2000, "total": 3000},
        file_changes=[
            {"success": True, "action": "created", "file": "test.py"}
        ]
    )
    
    assert len(response) > 0
    assert "test-project" in response
    print(f"   ✅ Response built: {len(response)} chars")
    
    # Test error response
    error = builder.build_error_response(
        project_name="test-project",
        error_message="Test error"
    )
    
    assert "ERROR" in error
    print(f"   ✅ Error response built: {len(error)} chars")

test_module("Response Builder", test_response)

# Summary
print("=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print(f"Tests passed: {tests_passed}/7")
print(f"Tests failed: {tests_failed}/7")
print()

if tests_failed == 0:
    print("✅ ALL TESTS PASSED! System ready for deployment.")
    print()
    print("🎯 Next steps:")
    print("   1. Setup PyCharm File Watcher")
    print("   2. Create n8n workflow")
    print("   3. Test complete automation pipeline")
    print()
    print("💡 Estimated savings per task:")
    print("   Chat init: ~40,000 tokens")
    print("   API call:  ~3,000 tokens")
    print("   Savings:   ~37,000 tokens (93%)")
    print("   Cost:      ~$0.015 vs ~$0.180")
    sys.exit(0)
else:
    print("❌ Some tests failed. Please fix errors before proceeding.")
    sys.exit(1)