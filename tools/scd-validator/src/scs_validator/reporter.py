"""Reporter module for formatting validation output."""

import json
from typing import Any, Dict, List

from colorama import Fore, Style, init

from .utils import ValidationResult

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class Reporter:
    """Formats and outputs validation results."""

    def __init__(self, use_color: bool = True):
        """Initialize reporter.

        Args:
            use_color: Whether to use colored output
        """
        self.use_color = use_color

    def report_text(
        self,
        results: List[ValidationResult],
        validator_version: str,
        strict: bool = False,
    ) -> str:
        """Generate text report of validation results.

        Args:
            results: List of validation results
            validator_version: Version of the validator
            strict: Whether strict mode is enabled

        Returns:
            Formatted text report
        """
        lines = []

        # Header
        lines.append(f"SCS Validator v{validator_version}")
        lines.append("")

        # Summary of each validation level
        total_errors = 0
        total_warnings = 0
        all_passed = True

        for result in results:
            status_symbol = self._check_mark() if result.passed else self._x_mark()
            status_text = "passed" if result.passed else "failed"

            line = f"{status_symbol} {result.level_name.capitalize()} validation {status_text}"

            # Add details if available
            if result.details:
                details_parts = []
                if "files_checked" in result.details:
                    details_parts.append(f"{result.details['files_checked']} files")
                if details_parts:
                    line += f" ({', '.join(details_parts)})"

            lines.append(line)

            total_errors += result.error_count
            total_warnings += result.warning_count

            if not result.passed:
                all_passed = False

        lines.append("")

        # Errors section
        if total_errors > 0:
            lines.append(self._colored("Errors:", Fore.RED))
            for result in results:
                for error in result.errors:
                    lines.append(f"  {self._x_mark()} {error.format_message()}")
            lines.append("")

        # Warnings section
        if total_warnings > 0:
            lines.append(self._colored("Warnings:", Fore.YELLOW))
            for result in results:
                for warning in result.warnings:
                    lines.append(f"  {self._warning_mark()} {str(warning)}")
            lines.append("")

        # Summary
        lines.append("Summary:")
        lines.append(f"  {total_errors} errors")
        lines.append(f"  {total_warnings} warnings")
        lines.append("")

        # Final status
        if all_passed and (not strict or total_warnings == 0):
            status_line = f"Status: {self._check_mark()} VALID"
            lines.append(self._colored(status_line, Fore.GREEN))
        elif all_passed and strict and total_warnings > 0:
            status_line = f"Status: {self._warning_mark()} VALID WITH WARNINGS (strict mode)"
            lines.append(self._colored(status_line, Fore.YELLOW))
        else:
            status_line = f"Status: {self._x_mark()} FAILED"
            lines.append(self._colored(status_line, Fore.RED))

        return "\n".join(lines)

    def report_json(
        self,
        results: List[ValidationResult],
        validator_version: str,
        strict: bool = False,
    ) -> str:
        """Generate JSON report of validation results.

        Args:
            results: List of validation results
            validator_version: Version of the validator
            strict: Whether strict mode is enabled

        Returns:
            JSON formatted report
        """
        total_errors = sum(r.error_count for r in results)
        total_warnings = sum(r.warning_count for r in results)
        all_passed = all(r.passed for r in results)

        # Determine overall status
        if all_passed and (not strict or total_warnings == 0):
            status = "valid"
        elif all_passed and strict and total_warnings > 0:
            status = "valid_with_warnings"
        else:
            status = "failed"

        report: Dict[str, Any] = {
            "validator_version": validator_version,
            "strict_mode": strict,
            "validation_levels": {},
            "errors": [],
            "warnings": [],
            "summary": {
                "total_errors": total_errors,
                "total_warnings": total_warnings,
                "status": status,
            },
        }

        # Add results for each validation level
        for result in results:
            level_data: Dict[str, Any] = {
                "status": "passed" if result.passed else "failed",
                "error_count": result.error_count,
                "warning_count": result.warning_count,
            }
            level_data.update(result.details)
            report["validation_levels"][result.level_name] = level_data

            # Add errors
            for error in result.errors:
                report["errors"].append(
                    {
                        "level": result.level_name,
                        "message": error.message,
                        "scd_id": error.scd_id,
                        "file_path": error.file_path,
                    }
                )

            # Add warnings
            for warning in result.warnings:
                report["warnings"].append(
                    {
                        "level": warning.level,
                        "message": warning.message,
                        "scd_id": warning.scd_id,
                        "file_path": warning.file_path,
                    }
                )

        return json.dumps(report, indent=2)

    def _check_mark(self) -> str:
        """Get check mark symbol."""
        return self._colored("✓", Fore.GREEN) if self.use_color else "✓"

    def _x_mark(self) -> str:
        """Get X mark symbol."""
        return self._colored("✗", Fore.RED) if self.use_color else "✗"

    def _warning_mark(self) -> str:
        """Get warning symbol."""
        return self._colored("⚠", Fore.YELLOW) if self.use_color else "⚠"

    def _colored(self, text: str, color: str) -> str:
        """Apply color to text if color is enabled."""
        if self.use_color:
            return f"{color}{text}{Style.RESET_ALL}"
        return text
