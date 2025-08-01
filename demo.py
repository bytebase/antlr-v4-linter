#!/usr/bin/env python3
"""Demo script to show ANTLR v4 linter functionality."""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from antlr_v4_linter import ANTLRLinter, LinterConfig

def main():
    """Run demo of the linter."""
    print("🔍 ANTLR v4 Linter Demo")
    print("=" * 50)
    
    # Create linter with default configuration
    linter = ANTLRLinter()
    
    # Test good grammar
    print("\n📄 Testing good_grammar.g4:")
    try:
        result = linter.lint_file("examples/good_grammar.g4")
        print(f"   Issues found: {result.total_issues}")
        if result.issues:
            for issue in result.issues:
                print(f"   • {issue.severity.value.upper()}: {issue.message} ({issue.rule_id})")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test bad grammar
    print("\n📄 Testing bad_grammar.g4:")
    try:
        result = linter.lint_file("examples/bad_grammar.g4")
        print(f"   Issues found: {result.total_issues}")
        print(f"   Errors: {result.error_count}, Warnings: {result.warning_count}, Info: {result.info_count}")
        
        if result.issues:
            print("\n   Issues:")
            for issue in result.issues:
                print(f"   • Line {issue.range.start.line}: {issue.severity.value.upper()} - {issue.message} ({issue.rule_id})")
                for suggestion in issue.suggestions:
                    print(f"     💡 {suggestion.description}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # List available rules
    print(f"\n📋 Available rules: {len(linter.get_rule_engine().rules)}")
    for rule in linter.get_rule_engine().rules:
        print(f"   • {rule.rule_id}: {rule.name}")
    
    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main()