#!/usr/bin/env python3
"""
Generate Financial Reports

Generate profit/loss statements, cash flow reports, and financial summaries
from accounting data.

Usage:
    python generate_report.py [--vault PATH] [--month YYYY-MM] [--type profit_loss]
"""

import argparse
import json
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FinancialReportGenerator:
    """Generate financial reports from accounting data."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.accounting_path = self.vault_path / "Accounting"
        self.business_goals_path = self.vault_path / "Business_Goals.md"

    def generate_profit_loss(self, month: str) -> dict:
        """
        Generate profit/loss statement for a month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            dict with profit/loss data
        """
        accounting_file = self.accounting_path / f"{month}.md"

        if not accounting_file.exists():
            logger.error(f"Accounting file not found: {accounting_file}")
            return {}

        content = accounting_file.read_text(encoding="utf-8")

        # Parse revenue section
        revenue_data = self._parse_revenue_section(content)

        # Parse expenses section
        expense_data = self._parse_expenses_section(content)

        # Calculate profit/loss
        total_revenue = revenue_data.get("total", 0)
        total_expenses = expense_data.get("total", 0)
        net_profit = total_revenue - total_expenses

        return {
            "month": month,
            "revenue": revenue_data,
            "expenses": expense_data,
            "profit_loss": {
                "gross_revenue": total_revenue,
                "total_expenses": total_expenses,
                "net_profit": net_profit,
                "profit_margin": (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            }
        }

    def _parse_revenue_section(self, content: str) -> dict:
        """Parse revenue section from accounting file."""
        lines = content.split("\n")

        revenue_by_source = []
        in_revenue_section = False
        total = 0

        for line in lines:
            if "## Revenue" in line:
                in_revenue_section = True
                continue

            if in_revenue_section:
                if line.startswith("|") and not line.startswith("|--"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 4 and parts[0] and parts[0] != "Source":
                        try:
                            amount = self._parse_currency(parts[1])
                            revenue_by_source.append({
                                "source": parts[0],
                                "amount": amount,
                                "invoices": parts[2],
                                "notes": parts[3]
                            })
                            total += amount
                        except:
                            pass
                elif line.startswith("**Total Revenue:**"):
                    total = self._parse_currency(line.split("**")[1].strip())
                elif line.startswith("##") and "Revenue" not in line:
                    break

        return {
            "by_source": revenue_by_source,
            "total": total
        }

    def _parse_expenses_section(self, content: str) -> dict:
        """Parse expenses section from accounting file."""
        lines = content.split("\n")

        expenses = []
        in_expenses_section = False
        total = 0

        for line in lines:
            if "## Expenses" in line:
                in_expenses_section = True
                continue

            if in_expenses_section:
                if line.startswith("|") and not line.startswith("|--"):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if len(parts) >= 3 and parts[0] and parts[0] != "Category":
                        try:
                            amount = self._parse_currency(parts[1])
                            expenses.append({
                                "category": parts[0],
                                "amount": amount,
                                "vendor": parts[2],
                                "date": parts[3] if len(parts) > 3 else ""
                            })
                            total += amount
                        except:
                            pass
                elif line.startswith("**Total Expenses:**"):
                    total = self._parse_currency(line.split("**")[1].strip())
                elif line.startswith("##") and "Expenses" not in line:
                    break

        # Group by category
        by_category = defaultdict(float)
        for expense in expenses:
            by_category[expense["category"]] += expense["amount"]

        return {
            "by_item": expenses,
            "by_category": dict(by_category),
            "total": total
        }

    def _parse_currency(self, value: str) -> float:
        """Parse currency string to float."""
        # Remove $, commas, and convert
        clean = value.replace("$", "").replace(",", "").strip()
        try:
            return float(clean)
        except:
            return 0.0

    def generate_report_text(self, data: dict) -> str:
        """Generate formatted report text."""
        if not data:
            return "No data available"

        report = f"""# Financial Report: {data['month']}

## Executive Summary

"""
        pl = data["profit_loss"]
        if pl["net_profit"] >= 0:
            report += f"✅ Profitable month with ${pl['net_profit']:,.2f} net profit ({pl['profit_margin']:.1f}% margin)\n\n"
        else:
            report += f"⚠️ Net loss of ${abs(pl['net_profit']):,.2f}\n\n"

        # Revenue section
        report += "## Revenue\n\n"
        report += f"**Total Revenue:** ${pl['gross_revenue']:,.2f}\n\n"

        if data["revenue"]["by_source"]:
            report += "### By Source\n"
            report += "| Source | Amount | Invoices | Notes |\n"
            report += "|--------|--------|----------|-------|\n"
            for source in data["revenue"]["by_source"]:
                report += f"| {source['source']} | ${source['amount']:,.2f} | {source['invoices']} | {source['notes']} |\n"

        # Expenses section
        report += "\n## Expenses\n\n"
        report += f"**Total Expenses:** ${pl['total_expenses']:,.2f}\n\n"

        if data["expenses"]["by_category"]:
            report += "### By Category\n"
            report += "| Category | Amount | Percentage |\n"
            report += "|----------|--------|------------|\n"
            for category, amount in sorted(data["expenses"]["by_category"].items(), key=lambda x: -x[1]):
                pct = (amount / pl['total_expenses'] * 100) if pl['total_expenses'] > 0 else 0
                report += f"| {category} | ${amount:,.2f} | {pct:.1f}% |\n"

        # Profit/Loss
        report += "\n## Profit & Loss\n\n"
        report += f"| | Amount |\n"
        report += f"|---|--------|\n"
        report += f"| **Gross Revenue** | ${pl['gross_revenue']:,.2f} |\n"
        report += f"| **Total Expenses** | (${pl['total_expenses']:,.2f}) |\n"
        report += f"| **Net Profit** | **${pl['net_profit']:,.2f}** |\n"
        report += f"| **Profit Margin** | **{pl['profit_margin']:.1f}%** |\n"

        # Top expenses
        if data["expenses"]["by_item"]:
            report += "\n### Top 5 Expenses\n"
            sorted_expenses = sorted(data["expenses"]["by_item"], key=lambda x: -x["amount"])[:5]
            report += "| Category | Vendor | Amount |\n"
            report += "|----------|--------|--------|\n"
            for expense in sorted_expenses:
                report += f"| {expense['category']} | {expense['vendor']} | ${expense['amount']:,.2f} |\n"

        report += f"\n---\n\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n"

        return report

    def save_report(self, month: str, output_path: Path = None) -> Path:
        """Generate and save report."""
        data = self.generate_profit_loss(month)
        report_text = self.generate_report_text(data)

        if output_path is None:
            output_path = self.accounting_path / f"report_{month}.md"

        output_path.write_text(report_text, encoding="utf-8")
        logger.info(f"Report saved to {output_path}")

        return output_path


def main():
    parser = argparse.ArgumentParser(description="Generate financial reports")
    parser.add_argument(
        "--vault",
        default=".",
        help="Path to vault (default: current directory)"
    )
    parser.add_argument(
        "--month",
        default=datetime.now().strftime("%Y-%m"),
        help="Month in YYYY-MM format (default: current month)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: Accounting/report_YYYY-MM.md)"
    )

    args = parser.parse_args()

    generator = FinancialReportGenerator(args.vault)
    report_path = generator.save_report(args.month, Path(args.output) if args.output else None)

    print(f"\n{'='*60}")
    print(f"Financial Report Generated")
    print(f"{'='*60}")
    print(f"Month: {args.month}")
    print(f"Output: {report_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
