import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Dict, List

from rich.console import Console
from rich.table import Table
from rich.text import Text

from .models import Issue, LintResult, Severity


class Reporter(ABC):
    """Base class for result reporters."""
    
    @abstractmethod
    def format_results(self, results: List[LintResult]) -> str:
        """Format lint results for output."""
        pass


class TextReporter(Reporter):
    """Reporter that formats results as human-readable text."""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        self.console = Console() if use_colors else None
    
    def format_results(self, results: List[LintResult]) -> str:
        """Format results as colored text output."""
        if not results:
            return "No files processed."
        
        output_lines = []
        total_issues = 0
        total_errors = 0
        total_warnings = 0
        total_info = 0
        
        for result in results:
            if result.issues:
                output_lines.append(f"\n{result.file_path}:")
                
                for issue in result.issues:
                    severity_symbol = self._get_severity_symbol(issue.severity)
                    location = f"{issue.range.start.line}:{issue.range.start.column}"
                    
                    line = f"  {location} {severity_symbol} {issue.message} ({issue.rule_id})"
                    output_lines.append(line)
                    
                    # Add fix suggestions if available
                    for suggestion in issue.suggestions:
                        output_lines.append(f"    💡 {suggestion.description}")
                        if suggestion.fix:
                            output_lines.append(f"       Fix: {suggestion.fix}")
            
            total_issues += result.total_issues
            total_errors += result.error_count
            total_warnings += result.warning_count
            total_info += result.info_count
        
        # Summary
        if total_issues > 0:
            output_lines.append("\n" + "=" * 50)
            output_lines.append(f"Total issues: {total_issues}")
            if total_errors > 0:
                output_lines.append(f"Errors: {total_errors}")
            if total_warnings > 0:
                output_lines.append(f"Warnings: {total_warnings}")
            if total_info > 0:
                output_lines.append(f"Info: {total_info}")
        else:
            output_lines.append("✅ No issues found!")
        
        return "\n".join(output_lines)
    
    def format_results_rich(self, results: List[LintResult]) -> None:
        """Format results using Rich formatting (for terminal output)."""
        if not self.console:
            print(self.format_results(results))
            return
        
        if not results:
            self.console.print("No files processed.", style="yellow")
            return
        
        total_issues = 0
        total_errors = 0
        total_warnings = 0
        total_info = 0
        
        for result in results:
            if result.issues:
                self.console.print(f"\n[bold]{result.file_path}[/bold]:")
                
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("Location", style="cyan")
                table.add_column("Severity", justify="center")
                table.add_column("Rule", style="blue")
                table.add_column("Message")
                
                for issue in result.issues:
                    location = f"{issue.range.start.line}:{issue.range.start.column}"
                    severity_text = Text(issue.severity.value.upper())
                    
                    if issue.severity == Severity.ERROR:
                        severity_text.stylize("bold red")
                    elif issue.severity == Severity.WARNING:
                        severity_text.stylize("bold yellow")
                    else:
                        severity_text.stylize("bold blue")
                    
                    table.add_row(location, severity_text, issue.rule_id, issue.message)
                
                self.console.print(table)
                
                # Show suggestions
                for issue in result.issues:
                    if issue.suggestions:
                        for suggestion in issue.suggestions:
                            self.console.print(f"    💡 [green]{suggestion.description}[/green]")
                            if suggestion.fix:
                                self.console.print(f"       [dim]Fix: {suggestion.fix}[/dim]")
            
            total_issues += result.total_issues
            total_errors += result.error_count
            total_warnings += result.warning_count
            total_info += result.info_count
        
        # Summary
        if total_issues > 0:
            self.console.print("\n" + "=" * 50, style="dim")
            self.console.print(f"[bold]Total issues: {total_issues}[/bold]")
            if total_errors > 0:
                self.console.print(f"[red]Errors: {total_errors}[/red]")
            if total_warnings > 0:
                self.console.print(f"[yellow]Warnings: {total_warnings}[/yellow]")
            if total_info > 0:
                self.console.print(f"[blue]Info: {total_info}[/blue]")
        else:
            self.console.print("✅ [green]No issues found![/green]")
    
    def _get_severity_symbol(self, severity: Severity) -> str:
        """Get symbol for severity level."""
        symbols = {
            Severity.ERROR: "❌",
            Severity.WARNING: "⚠️",
            Severity.INFO: "ℹ️"
        }
        return symbols.get(severity, "•")


class JsonReporter(Reporter):
    """Reporter that formats results as JSON."""
    
    def format_results(self, results: List[LintResult]) -> str:
        """Format results as JSON."""
        output = {
            "results": [],
            "summary": {
                "totalFiles": len(results),
                "totalIssues": 0,
                "errorCount": 0,
                "warningCount": 0,
                "infoCount": 0
            }
        }
        
        for result in results:
            file_result = {
                "file": result.file_path,
                "issues": [
                    {
                        "ruleId": issue.rule_id,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "line": issue.range.start.line,
                        "column": issue.range.start.column,
                        "endLine": issue.range.end.line,
                        "endColumn": issue.range.end.column,
                        "suggestions": [
                            {
                                "description": suggestion.description,
                                "fix": suggestion.fix
                            }
                            for suggestion in issue.suggestions
                        ]
                    }
                    for issue in result.issues
                ],
                "summary": {
                    "totalIssues": result.total_issues,
                    "errorCount": result.error_count,
                    "warningCount": result.warning_count,
                    "infoCount": result.info_count
                }
            }
            output["results"].append(file_result)
            
            # Update global summary
            output["summary"]["totalIssues"] += result.total_issues
            output["summary"]["errorCount"] += result.error_count
            output["summary"]["warningCount"] += result.warning_count
            output["summary"]["infoCount"] += result.info_count
        
        return json.dumps(output, indent=2)


class XmlReporter(Reporter):
    """Reporter that formats results as XML."""
    
    def format_results(self, results: List[LintResult]) -> str:
        """Format results as XML."""
        root = ET.Element("lintResults")
        
        # Summary
        summary = ET.SubElement(root, "summary")
        total_files = len(results)
        total_issues = sum(result.total_issues for result in results)
        total_errors = sum(result.error_count for result in results)
        total_warnings = sum(result.warning_count for result in results)
        total_info = sum(result.info_count for result in results)
        
        ET.SubElement(summary, "totalFiles").text = str(total_files)
        ET.SubElement(summary, "totalIssues").text = str(total_issues)
        ET.SubElement(summary, "errorCount").text = str(total_errors)
        ET.SubElement(summary, "warningCount").text = str(total_warnings)
        ET.SubElement(summary, "infoCount").text = str(total_info)
        
        # Results
        results_elem = ET.SubElement(root, "results")
        
        for result in results:
            file_elem = ET.SubElement(results_elem, "file")
            file_elem.set("path", result.file_path)
            
            for issue in result.issues:
                issue_elem = ET.SubElement(file_elem, "issue")
                issue_elem.set("ruleId", issue.rule_id)
                issue_elem.set("severity", issue.severity.value)
                issue_elem.set("line", str(issue.range.start.line))
                issue_elem.set("column", str(issue.range.start.column))
                
                ET.SubElement(issue_elem, "message").text = issue.message
                
                if issue.suggestions:
                    suggestions_elem = ET.SubElement(issue_elem, "suggestions")
                    for suggestion in issue.suggestions:
                        suggestion_elem = ET.SubElement(suggestions_elem, "suggestion")
                        ET.SubElement(suggestion_elem, "description").text = suggestion.description
                        if suggestion.fix:
                            ET.SubElement(suggestion_elem, "fix").text = suggestion.fix
        
        return ET.tostring(root, encoding='unicode')


class ReporterFactory:
    """Factory for creating reporters."""
    
    _reporters: Dict[str, type] = {
        "text": TextReporter,
        "json": JsonReporter,
        "xml": XmlReporter,
    }
    
    @classmethod
    def create_reporter(cls, format_name: str, **kwargs) -> Reporter:
        """Create a reporter instance."""
        if format_name not in cls._reporters:
            raise ValueError(f"Unknown format: {format_name}. Available: {list(cls._reporters.keys())}")
        
        return cls._reporters[format_name](**kwargs)
    
    @classmethod
    def available_formats(cls) -> List[str]:
        """Get list of available output formats."""
        return list(cls._reporters.keys())