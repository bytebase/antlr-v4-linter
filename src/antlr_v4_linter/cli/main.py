"""Main CLI entry point for ANTLR v4 linter."""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console

from ..core.config import ConfigValidator, create_default_config_file, load_config
from ..core.linter import ANTLRLinter
from ..core.reporter import ReporterFactory


@click.group()
@click.version_option(version="0.1.1", prog_name="antlr-lint")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose):
    """ANTLR v4 Grammar Linter - Static analysis for .g4 files."""
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose


@cli.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--format", "-f", "output_format", 
              type=click.Choice(ReporterFactory.available_formats()),
              help="Output format")
@click.option("--no-colors", is_flag=True, help="Disable colored output")
@click.option("--exclude", multiple=True, help="Exclude patterns (can be used multiple times)")
@click.option("--rule", multiple=True, help="Enable specific rules (can be used multiple times)")
@click.option("--disable-rule", multiple=True, help="Disable specific rules (can be used multiple times)")
@click.option("--severity", type=click.Choice(["error", "warning", "info"]), 
              help="Minimum severity level to report")
@click.pass_context
def lint(ctx, files, config, output_format, no_colors, exclude, rule, disable_rule, severity):
    """Lint ANTLR v4 grammar files."""
    verbose = ctx.obj.get('verbose', False)
    console = Console() if not no_colors else Console(color_system=None)
    
    try:
        # Load configuration
        linter_config = load_config(config)
        
        # Apply CLI overrides
        if output_format:
            linter_config.output_format = output_format
        
        if exclude:
            linter_config.exclude_patterns.extend(exclude)
        
        # Handle rule overrides
        if rule:
            # Disable all rules first, then enable specified ones
            for rule_id in linter_config.rules:
                linter_config.rules[rule_id].enabled = False
            for rule_id in rule:
                if rule_id in linter_config.rules:
                    linter_config.rules[rule_id].enabled = True
                else:
                    console.print(f"[yellow]Warning: Unknown rule '{rule_id}'[/yellow]")
        
        if disable_rule:
            for rule_id in disable_rule:
                if rule_id in linter_config.rules:
                    linter_config.rules[rule_id].enabled = False
                else:
                    console.print(f"[yellow]Warning: Unknown rule '{rule_id}'[/yellow]")
        
        # Validate configuration
        config_errors = ConfigValidator.validate_config(linter_config)
        if config_errors:
            console.print("[red]Configuration errors:[/red]")
            for error in config_errors:
                console.print(f"  • {error}")
            sys.exit(1)
        
        # Expand file paths and find .g4 files
        file_paths = _expand_file_paths(files)
        
        if not file_paths:
            console.print("[yellow]No .g4 files found[/yellow]")
            sys.exit(0)
        
        if verbose:
            console.print(f"Found {len(file_paths)} files to lint:")
            for file_path in file_paths:
                console.print(f"  • {file_path}")
            console.print()
        
        # Create linter and run
        linter = ANTLRLinter(linter_config)
        results = linter.lint_files(file_paths)
        
        # Filter by severity if specified
        if severity:
            from ..core.models import Severity
            min_severity = Severity(severity)
            severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}
            min_level = severity_order[min_severity]
            
            for result in results:
                result.issues = [
                    issue for issue in result.issues 
                    if severity_order[issue.severity] >= min_level
                ]
        
        # Output results
        if linter_config.output_format == "text":
            linter.print_results(results, use_colors=not no_colors)
        else:
            output = linter.format_results(results, linter_config.output_format)
            console.print(output)
        
        # Exit with error code if there are errors
        total_errors = sum(result.error_count for result in results)
        if total_errors > 0:
            sys.exit(1)
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.argument("output_path", type=click.Path(), default="antlr-lint.json")
@click.option("--overwrite", is_flag=True, help="Overwrite existing configuration file")
def init(output_path, overwrite):
    """Initialize a new configuration file."""
    console = Console()
    
    output_file = Path(output_path)
    
    if output_file.exists() and not overwrite:
        console.print(f"[red]Configuration file already exists: {output_path}[/red]")
        console.print("Use --overwrite to replace it")
        sys.exit(1)
    
    try:
        create_default_config_file(output_path)
        console.print(f"[green]Created configuration file: {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error creating configuration file: {e}[/red]")
        sys.exit(1)


@cli.command()
def rules():
    """List all available linting rules."""
    console = Console()
    
    # Create linter to get rule information
    linter = ANTLRLinter()
    rule_engine = linter.get_rule_engine()
    
    console.print("[bold]Available Linting Rules:[/bold]\n")
    
    categories = {
        "S": "Syntax and Structure",
        "N": "Naming and Convention", 
        "L": "Labeling and Organization",
        "C": "Complexity and Maintainability",
        "T": "Token and Lexer",
        "E": "Error Handling",
        "P": "Performance",
        "D": "Documentation"
    }
    
    rules_by_category = {}
    for rule in rule_engine.rules:
        category = rule.rule_id[0]
        if category not in rules_by_category:
            rules_by_category[category] = []
        rules_by_category[category].append(rule)
    
    for category_code, category_name in categories.items():
        if category_code in rules_by_category:
            console.print(f"[bold cyan]{category_name}:[/bold cyan]")
            for rule in sorted(rules_by_category[category_code], key=lambda r: r.rule_id):
                console.print(f"  [blue]{rule.rule_id}[/blue]: {rule.name}")
                console.print(f"    {rule.description}")
            console.print()


@cli.command()
@click.argument("config_path", type=click.Path(exists=True))
def validate_config(config_path):
    """Validate a configuration file."""
    console = Console()
    
    try:
        config = load_config(config_path)
        errors = ConfigValidator.validate_config(config)
        
        if errors:
            console.print(f"[red]Configuration file '{config_path}' has errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            sys.exit(1)
        else:
            console.print(f"[green]Configuration file '{config_path}' is valid[/green]")
    
    except Exception as e:
        console.print(f"[red]Error validating configuration: {e}[/red]")
        sys.exit(1)


def _expand_file_paths(file_paths: tuple) -> List[str]:
    """Expand file paths to find all .g4 files."""
    expanded = []
    
    for file_path in file_paths:
        path = Path(file_path)
        
        if path.is_file():
            if path.suffix == '.g4':
                expanded.append(str(path))
        elif path.is_dir():
            # Find all .g4 files recursively
            for g4_file in path.rglob("*.g4"):
                expanded.append(str(g4_file))
    
    return sorted(expanded)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()