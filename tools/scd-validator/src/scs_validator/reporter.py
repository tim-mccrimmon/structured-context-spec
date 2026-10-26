"""Reporter module for formatting validation output."""

import json
from typing import TYPE_CHECKING, Any, Dict, List

from colorama import Fore, Style, init

from .utils import ValidationResult

if TYPE_CHECKING:
    from .api import Report

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
        report: "Report",
        validator_version: str,
        strict: bool = False,
    ) -> str:
        """Generate text report of validation results.

        Args:
            report: Validation report
            validator_version: Version of the validator
            strict: Whether strict mode is enabled

        Returns:
            Formatted text report
        """
        lines = [f"SCS Validator v{validator_version}", ""]
        if report.repository is not None:
            lines.append(f"Repository: {report.repository}")
            lines.append("")
            lines.extend(self._text_section(report.results, show_levels=False))
            for workspace in report.workspaces:
                lines.append(self._colored(f"Workspace {workspace.name}", Style.BRIGHT))
                lines.extend(self._text_section(workspace.results))
        else:
            lines.extend(self._text_section(report.results))

        results = report.all_results()
        total_errors = sum(r.error_count for r in results)
        total_warnings = sum(r.warning_count for r in results)
        all_passed = all(r.passed for r in results)

        lines.append("Summary:")
        lines.append(f"  {total_errors} errors")
        lines.append(f"  {total_warnings} warnings")
        infos = sum(len(r.infos) for r in results)
        if infos:
            lines.append(f"  {infos} info")
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

    def _text_section(self, results: List[ValidationResult], show_levels: bool = True) -> List[str]:
        """Level summary, then errors, warnings, and info for one set of results."""
        lines = []
        if show_levels:
            for result in results:
                status_symbol = self._check_mark() if result.passed else self._x_mark()
                status_text = "passed" if result.passed else "failed"
                name = result.level_name.capitalize()
                line = f"{status_symbol} {name} validation {status_text}"
                if "files_checked" in result.details:
                    line += f" ({result.details['files_checked']} files)"
                lines.append(line)
            lines.append("")

        errors = [e for r in results for e in r.errors]
        warnings = [w for r in results for w in r.warnings]
        infos = [i for r in results for i in r.infos]
        if errors:
            lines.append(self._colored("Errors:", Fore.RED))
            lines.extend(f"  {self._x_mark()} {e.format_message()}" for e in errors)
            lines.append("")
        if warnings:
            lines.append(self._colored("Warnings:", Fore.YELLOW))
            lines.extend(f"  {self._warning_mark()} {w}" for w in warnings)
            lines.append("")
        if infos:
            lines.append("Info:")
            lines.extend(f"  i {i}" for i in infos)
            lines.append("")
        return lines

    def report_json(
        self,
        report: "Report",
        validator_version: str,
        strict: bool = False,
    ) -> str:
        """Generate JSON report of validation results (schema/validator/report-schema.json).

        Args:
            report: Validation report
            validator_version: Version of the validator
            strict: Whether strict mode is enabled

        Returns:
            JSON formatted report
        """
        data: Dict[str, Any] = {"validator_version": validator_version, "strict_mode": strict}
        data.update(self._json_section(report.results, strict))
        if report.repository is not None:
            data["repository"] = str(report.repository)
            data["workspaces"] = [
                {"name": w.name, "path": str(w.path), **self._json_section(w.results, strict)}
                for w in report.workspaces
            ]
            data["summary"] = self._json_summary(report.all_results(), strict)
        return json.dumps(data, indent=2)

    def _json_section(self, results: List[ValidationResult], strict: bool) -> Dict[str, Any]:
        levels: Dict[str, Any] = {}
        errors: List[Dict[str, Any]] = []
        warnings: List[Dict[str, Any]] = []
        infos: List[Dict[str, Any]] = []
        for result in results:
            level_data: Dict[str, Any] = {
                "status": "passed" if result.passed else "failed",
                "error_count": result.error_count,
                "warning_count": result.warning_count,
            }
            level_data.update(result.details)
            levels[result.level_name] = level_data
            errors.extend(self._finding(result.level_name, e) for e in result.errors)
            warnings.extend(self._finding(w.level, w) for w in result.warnings)
            infos.extend(self._finding(i.level, i) for i in result.infos)
        return {
            "validation_levels": levels,
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "summary": self._json_summary(results, strict),
        }

    @staticmethod
    def _finding(level: str, diagnostic: Any) -> Dict[str, Any]:
        return {
            "level": level,
            "severity": diagnostic.severity,
            "code": diagnostic.code,
            "message": diagnostic.message,
            "scd_id": diagnostic.scd_id,
            "file_path": diagnostic.file_path,
        }

    @staticmethod
    def _json_summary(results: List[ValidationResult], strict: bool) -> Dict[str, Any]:
        total_warnings = sum(r.warning_count for r in results)
        all_passed = all(r.passed for r in results)
        if all_passed and (not strict or total_warnings == 0):
            status = "valid"
        elif all_passed and strict:
            status = "valid_with_warnings"
        else:
            status = "failed"
        return {
            "total_errors": sum(r.error_count for r in results),
            "total_warnings": total_warnings,
            "total_infos": sum(len(r.infos) for r in results),
            "status": status,
        }

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
