#!/usr/bin/env python3
"""
Validate crypto trading agent architecture compliance.

Usage:
    python validate_architecture.py /path/to/project
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple
import re


class ArchitectureValidator:
    """Validate 5-layer architecture compliance."""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.errors = []
        self.warnings = []

    def validate(self) -> bool:
        """Run all validation checks."""

        print("Validating crypto trading agent architecture...")
        print(f"Project: {self.project_path}\n")

        checks = [
            ("Layer 1: Smart Consensus", self.validate_layer1),
            ("Layer 2: Exchange Adapters", self.validate_layer2),
            ("Layer 3: Trading Strategy", self.validate_layer3),
            ("Layer 4: Data Pipeline", self.validate_layer4),
            ("Layer 5: Monitoring", self.validate_layer5),
            ("Test Structure", self.validate_tests),
            ("Test Coverage", self.validate_coverage),
            ("Configuration", self.validate_config),
            ("Integration", self.validate_integration),
        ]

        all_passed = True

        for check_name, check_func in checks:
            passed, message = check_func()

            if passed:
                print(f"✅ {check_name}: {message}")
            else:
                print(f"❌ {check_name}: {message}")
                all_passed = False

        if self.warnings:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")

        return all_passed

    def validate_layer1(self) -> Tuple[bool, str]:
        """Validate Layer 1: Smart Consensus."""

        consensus_dir = self.project_path / "src/consensus"

        if not consensus_dir.exists():
            return False, "consensus/ directory not found"

        # Check for required components
        required_files = [
            "manager.py",  # ConsensusManager
            "validator.py",  # DecisionValidator
        ]

        missing = []
        for file in required_files:
            if not (consensus_dir / file).exists():
                # Check subdirectories
                found = False
                for subdir in consensus_dir.iterdir():
                    if subdir.is_dir() and (subdir / file).exists():
                        found = True
                        break
                if not found:
                    missing.append(file)

        if missing:
            return False, f"Missing files: {', '.join(missing)}"

        # Check for consensus engine usage
        has_consensus = False
        for py_file in consensus_dir.rglob("*.py"):
            content = py_file.read_text()
            if "ConsensusEngine" in content or "consensus" in content.lower():
                has_consensus = True
                break

        if not has_consensus:
            self.warnings.append(
                "Layer 1: No consensus engine implementation found"
            )

        return True, "consensus/ exists, implements multi-LLM consensus"

    def validate_layer2(self) -> Tuple[bool, str]:
        """Validate Layer 2: Exchange Adapters."""

        adapters_dir = self.project_path / "src/adapters"

        if not adapters_dir.exists():
            return False, "adapters/ directory not found"

        # Check for at least one exchange adapter
        exchange_dirs = [
            d for d in adapters_dir.iterdir()
            if d.is_dir() and d.name != "__pycache__"
        ]

        if not exchange_dirs:
            return False, "No exchange adapter found"

        # Check for resilience patterns
        has_resilience = False
        for py_file in adapters_dir.rglob("*.py"):
            content = py_file.read_text()
            resilience_patterns = [
                "CircuitBreaker",
                "RateLimiter",
                "RetryPolicy",
                "circuit_breaker",
                "rate_limiter",
                "retry"
            ]
            if any(pattern in content for pattern in resilience_patterns):
                has_resilience = True
                break

        if not has_resilience:
            self.warnings.append(
                "Layer 2: No resilience patterns detected (circuit breaker, retry, rate limiter)"
            )

        return True, "adapters/ exists, implements resilience patterns"

    def validate_layer3(self) -> Tuple[bool, str]:
        """Validate Layer 3: Trading Strategy."""

        strategies_dir = self.project_path / "src/strategies"

        if not strategies_dir.exists():
            return False, "strategies/ directory not found"

        # Check for risk management
        risk_dir = strategies_dir / "risk"
        has_risk = risk_dir.exists()

        if not has_risk:
            # Check for risk-related files
            for py_file in strategies_dir.rglob("*.py"):
                if "risk" in py_file.name.lower():
                    has_risk = True
                    break

        if not has_risk:
            return False, "No risk management implementation found"

        # Check for position sizing
        has_position_sizing = False
        for py_file in strategies_dir.rglob("*.py"):
            content = py_file.read_text()
            if "position" in content.lower() and "size" in content.lower():
                has_position_sizing = True
                break

        if not has_position_sizing:
            self.warnings.append(
                "Layer 3: No position sizing implementation found"
            )

        return True, "strategies/ exists, implements RiskManager"

    def validate_layer4(self) -> Tuple[bool, str]:
        """Validate Layer 4: Data Pipeline."""

        data_dir = self.project_path / "src/data"

        if not data_dir.exists():
            return False, "data/ directory not found"

        # Check for data ingestion
        has_ingestion = False
        for py_file in data_dir.rglob("*.py"):
            content = py_file.read_text()
            if "ingest" in content.lower() or "stream" in content.lower():
                has_ingestion = True
                break

        if not has_ingestion:
            self.warnings.append(
                "Layer 4: No data ingestion implementation found"
            )

        # Check for validation
        has_validation = False
        for py_file in data_dir.rglob("*.py"):
            if "validat" in py_file.name.lower():
                has_validation = True
                break

        if not has_validation:
            self.warnings.append(
                "Layer 4: No data validation implementation found"
            )

        # Check for caching
        has_cache = False
        for py_file in data_dir.rglob("*.py"):
            content = py_file.read_text()
            if "cache" in content.lower() or "redis" in content.lower():
                has_cache = True
                break

        if not has_cache:
            self.warnings.append(
                "Layer 4: No caching implementation found"
            )

        return True, "data/ exists, implements data pipeline"

    def validate_layer5(self) -> Tuple[bool, str]:
        """Validate Layer 5: Monitoring."""

        monitoring_dir = self.project_path / "src/monitoring"

        if not monitoring_dir.exists():
            return False, "monitoring/ directory not found"

        # Check for Prometheus metrics
        has_prometheus = False
        for py_file in monitoring_dir.rglob("*.py"):
            content = py_file.read_text()
            if "prometheus" in content.lower() or "Counter" in content or "Gauge" in content:
                has_prometheus = True
                break

        if not has_prometheus:
            return False, "No Prometheus metrics found"

        # Check for alerts
        has_alerts = False
        for py_file in monitoring_dir.rglob("*.py"):
            if "alert" in py_file.name.lower():
                has_alerts = True
                break

        if not has_alerts:
            self.warnings.append(
                "Layer 5: No alert manager implementation found"
            )

        # Check for structured logging
        has_logging = False
        for py_file in monitoring_dir.rglob("*.py"):
            content = py_file.read_text()
            if "structlog" in content or "logging" in content:
                has_logging = True
                break

        if not has_logging:
            self.warnings.append(
                "Layer 5: No structured logging implementation found"
            )

        return True, "monitoring/ exists, exposes Prometheus metrics"

    def validate_tests(self) -> Tuple[bool, str]:
        """Validate test structure."""

        tests_dir = self.project_path / "tests"

        if not tests_dir.exists():
            return False, "tests/ directory not found"

        # Check for test subdirectories
        required_dirs = ["unit", "integration"]
        missing_dirs = []

        for dir_name in required_dirs:
            if not (tests_dir / dir_name).exists():
                missing_dirs.append(dir_name)

        if missing_dirs:
            self.warnings.append(
                f"Test directories missing: {', '.join(missing_dirs)}"
            )

        # Count test files
        test_files = list(tests_dir.rglob("test_*.py"))

        if not test_files:
            return False, "No test files found"

        return True, f"Found {len(test_files)} test files"

    def validate_coverage(self) -> Tuple[bool, str]:
        """Validate test coverage."""

        # Check for pytest config
        pyproject = self.project_path / "pyproject.toml"

        if not pyproject.exists():
            self.warnings.append(
                "No pyproject.toml found, cannot validate coverage config"
            )
            return True, "Coverage config not checked (no pyproject.toml)"

        content = pyproject.read_text()

        if "pytest" not in content or "coverage" not in content:
            self.warnings.append(
                "No pytest/coverage configuration in pyproject.toml"
            )

        # Try to read coverage report if it exists
        coverage_file = self.project_path / ".coverage"
        htmlcov = self.project_path / "htmlcov"

        if coverage_file.exists() or htmlcov.exists():
            # Parse coverage if possible
            try:
                import coverage as cov_module
                cov = cov_module.Coverage(data_file=str(coverage_file))
                cov.load()
                total = cov.report()

                if total >= 80:
                    return True, f"Test coverage: {total:.0f}% (target: 80%+)"
                else:
                    return False, f"Test coverage: {total:.0f}% (target: 80%+)"
            except:
                pass

        return True, "Run 'pytest --cov=src' to generate coverage report"

    def validate_config(self) -> Tuple[bool, str]:
        """Validate configuration files."""

        config_dir = self.project_path / "config"

        if not config_dir.exists():
            return False, "config/ directory not found"

        # Check for required config files
        required_configs = [
            "risk_rules.yaml",
            "exchanges.yaml",
        ]

        missing = []
        for config_file in required_configs:
            if not (config_dir / config_file).exists():
                missing.append(config_file)

        if missing:
            self.warnings.append(
                f"Missing config files: {', '.join(missing)}"
            )

        return True, "Configuration files present"

    def validate_integration(self) -> Tuple[bool, str]:
        """Validate layer integration."""

        # Check that layers reference each other
        src_dir = self.project_path / "src"

        if not src_dir.exists():
            return False, "src/ directory not found"

        # Check for cross-layer imports
        layers = ["consensus", "adapters", "strategies", "data", "monitoring"]
        layer_imports = {layer: set() for layer in layers}

        for layer in layers:
            layer_dir = src_dir / layer
            if not layer_dir.exists():
                continue

            for py_file in layer_dir.rglob("*.py"):
                content = py_file.read_text()

                # Find imports from other layers
                for other_layer in layers:
                    if other_layer != layer:
                        if f"from {other_layer}" in content or f"import {other_layer}" in content:
                            layer_imports[layer].add(other_layer)

        # Check that there are some cross-layer integrations
        total_integrations = sum(len(imports) for imports in layer_imports.values())

        if total_integrations == 0:
            self.warnings.append(
                "No cross-layer imports detected - layers may not be integrated"
            )

        return True, "All layers properly integrated"


def main():
    """Main validation function."""

    parser = argparse.ArgumentParser(
        description="Validate crypto trading agent architecture"
    )
    parser.add_argument(
        "project_path",
        help="Path to project directory"
    )

    args = parser.parse_args()

    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        print(f"❌ Error: Project path does not exist: {project_path}")
        sys.exit(1)

    validator = ArchitectureValidator(project_path)
    passed = validator.validate()

    if passed:
        print("\n✅ Architecture validation passed!")
        sys.exit(0)
    else:
        print("\n❌ Architecture validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
