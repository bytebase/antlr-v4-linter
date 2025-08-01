"""Configuration management for ANTLR v4 linter."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import LinterConfig, RuleConfig, Severity


class ConfigLoader:
    """Loads and validates linter configuration from various sources."""
    
    @staticmethod
    def load_from_file(config_path: str) -> LinterConfig:
        """Load configuration from a JSON file."""
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return ConfigLoader._parse_config_data(data)
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")
    
    @staticmethod
    def load_from_dict(data: Dict[str, Any]) -> LinterConfig:
        """Load configuration from a dictionary."""
        return ConfigLoader._parse_config_data(data)
    
    @staticmethod
    def find_config_file(start_dir: str = ".") -> Optional[str]:
        """Find configuration file in directory hierarchy."""
        config_names = [
            "antlr-lint.json",
            ".antlr-lint.json", 
            "antlr-linter.json",
            ".antlr-linter.json"
        ]
        
        current_dir = Path(start_dir).resolve()
        
        # Look up the directory tree
        while current_dir != current_dir.parent:
            for config_name in config_names:
                config_path = current_dir / config_name
                if config_path.exists():
                    return str(config_path)
            current_dir = current_dir.parent
        
        return None
    
    @staticmethod
    def _parse_config_data(data: Dict[str, Any]) -> LinterConfig:
        """Parse configuration data into LinterConfig object."""
        config = LinterConfig()
        
        # Parse rules configuration
        if "rules" in data:
            rules_data = data["rules"]
            for rule_id, rule_config in rules_data.items():
                if isinstance(rule_config, dict):
                    # Full rule configuration
                    config.rules[rule_id] = RuleConfig(
                        enabled=rule_config.get("enabled", True),
                        severity=Severity(rule_config.get("severity", "warning")),
                        thresholds=rule_config.get("thresholds", {})
                    )
                elif isinstance(rule_config, bool):
                    # Simple boolean configuration
                    config.rules[rule_id] = RuleConfig(enabled=rule_config)
                elif isinstance(rule_config, str):
                    # Severity-only configuration
                    config.rules[rule_id] = RuleConfig(severity=Severity(rule_config))
        
        # Parse exclude patterns
        if "excludePatterns" in data:
            config.exclude_patterns = data["excludePatterns"]
        
        # Parse output format
        if "outputFormat" in data:
            config.output_format = data["outputFormat"]
        
        return config
    
    @staticmethod
    def save_to_file(config: LinterConfig, config_path: str) -> None:
        """Save configuration to a JSON file."""
        data = ConfigLoader._config_to_dict(config)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def _config_to_dict(config: LinterConfig) -> Dict[str, Any]:
        """Convert LinterConfig to dictionary."""
        data = {
            "rules": {},
            "excludePatterns": config.exclude_patterns,
            "outputFormat": config.output_format
        }
        
        for rule_id, rule_config in config.rules.items():
            data["rules"][rule_id] = {
                "enabled": rule_config.enabled,
                "severity": rule_config.severity.value
            }
            
            if rule_config.thresholds:
                data["rules"][rule_id]["thresholds"] = rule_config.thresholds
        
        return data


class ConfigValidator:
    """Validates linter configuration."""
    
    VALID_SEVERITIES = {"error", "warning", "info"}
    VALID_OUTPUT_FORMATS = {"text", "json", "xml"}
    
    # Known rule IDs (will be expanded as more rules are added)
    KNOWN_RULE_IDS = {
        # Syntax and Structure
        "S001", "S002", "S003",
        # Naming and Convention  
        "N001", "N002", "N003",
        # Labeling and Organization (future)
        "L001", "L002", "L003",
        # Complexity and Maintainability (future)
        "C001", "C002", "C003",
        # Token and Lexer (future)
        "T001", "T002", "T003",
        # Error Handling (future)
        "E001", "E002",
        # Performance (future)
        "P001", "P002",
        # Documentation (future)
        "D001", "D002",
    }
    
    @classmethod
    def validate_config(cls, config: LinterConfig) -> List[str]:
        """Validate configuration and return list of validation errors."""
        errors = []
        
        # Validate output format
        if config.output_format not in cls.VALID_OUTPUT_FORMATS:
            errors.append(f"Invalid output format '{config.output_format}'. "
                         f"Valid options: {', '.join(cls.VALID_OUTPUT_FORMATS)}")
        
        # Validate rules
        for rule_id, rule_config in config.rules.items():
            # Check if rule ID is known
            if rule_id not in cls.KNOWN_RULE_IDS:
                errors.append(f"Unknown rule ID '{rule_id}'")
            
            # Validate severity
            if rule_config.severity.value not in cls.VALID_SEVERITIES:
                errors.append(f"Invalid severity '{rule_config.severity.value}' for rule {rule_id}. "
                             f"Valid options: {', '.join(cls.VALID_SEVERITIES)}")
        
        # Validate exclude patterns (basic check)
        for pattern in config.exclude_patterns:
            if not isinstance(pattern, str):
                errors.append(f"Exclude pattern must be a string, got {type(pattern)}")
        
        return errors
    
    @classmethod
    def validate_rule_thresholds(cls, rule_id: str, thresholds: Dict[str, Any]) -> List[str]:
        """Validate rule-specific threshold values."""
        errors = []
        
        # Rule-specific threshold validation
        if rule_id == "C001":  # Complexity rule
            expected_thresholds = {"maxAlternatives", "maxNestingDepth", "maxTokens"}
            for key, value in thresholds.items():
                if key in expected_thresholds:
                    if not isinstance(value, int) or value <= 0:
                        errors.append(f"Threshold '{key}' for rule {rule_id} must be a positive integer")
        
        return errors


def create_default_config_file(file_path: str) -> None:
    """Create a default configuration file."""
    config = LinterConfig.default()
    ConfigLoader.save_to_file(config, file_path)


def load_config(config_path: Optional[str] = None) -> LinterConfig:
    """Load configuration with automatic discovery."""
    if config_path:
        # Use explicitly provided config file
        return ConfigLoader.load_from_file(config_path)
    
    # Try to find config file automatically
    found_config = ConfigLoader.find_config_file()
    if found_config:
        return ConfigLoader.load_from_file(found_config)
    
    # Use default configuration
    return LinterConfig.default()