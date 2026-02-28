#!/usr/bin/env python3
"""
GLM-Powered Auto-Approval Processor for AI Employee

Uses GLM AI to intelligently decide which actions to auto-approve
based on Company_Handbook.md rules and context.

Usage:
    python scripts/auto_approver_glm.py --vault AI_Employee_Vault
"""

import json
import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


class GLMApprover:
    """AI-powered approval decisions using GLM (Zhipu AI)."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.rejected = self.vault_path / "Rejected"
        self.done = self.vault_path / "Done"

        # Ensure folders exist
        for folder in [self.needs_action, self.pending_approval, self.approved, self.rejected, self.done]:
            folder.mkdir(parents=True, exist_ok=True)

        # Load Company Handbook rules
        self.handbook_rules = self._load_handbook_rules()

        # Load GLM API credentials
        self.api_key = os.getenv("GLM_API_KEY")
        self.api_url = os.getenv("GLM_API_URL", "https://api.z.ai/api/paas/v4")

    def _load_handbook_rules(self) -> str:
        """Load Company_Handbook.md to provide context to GLM."""
        handbook_path = self.vault_path / "Company_Handbook.md"

        if handbook_path.exists():
            return handbook_path.read_text(encoding='utf-8')
        else:
            return """
# Default Company Handbook Rules

## Permission Boundaries
- Auto-approve: Routine tasks, file operations, known contact emails
- Manual review required: Payments, social media, new contacts, high-value actions
- Reject: Scams, phishing, dangerous actions

## Safety First
When in doubt, require manual review. It's better to ask for approval than to make a mistake.
"""

    def _ask_glm_for_decision(self, frontmatter: Dict, content: str, filepath: Path) -> str:
        """
        Ask GLM AI to make an approval decision.

        Returns:
            "approve" - Safe to auto-approve
            "reject" - Unsafe, should be rejected
            "manual" - Needs human review
        """
        if not self.api_key:
            # Fallback to simple rules if no API key
            return self._fallback_decision(frontmatter, content, filepath)

        try:
            import requests

            # Build prompt with context
            prompt = f"""You are an AI assistant that decides whether to auto-approve actions based on company rules.

# COMPANY HANDBOOK RULES
{self.handbook_rules[:3000]}

# ACTION TO EVALUATE
Type: {frontmatter.get('type', 'unknown')}
Service: {frontmatter.get('service', 'unknown')}
Priority: {frontmatter.get('priority', 'normal')}
From: {frontmatter.get('from', 'unknown')}
Subject: {frontmatter.get('subject', 'N/A')}

# CONTENT
{content[:2000]}

# DECISION FRAMEWORK
Respond with ONLY one word:
- "approve" - Safe, routine action within established rules
- "reject" - Dangerous, scam, phishing, or violates rules
- "manual" - Requires human review (uncertain, high-value, or first-time action)

Your decision:"""

            # GLM API call (OpenAI-compatible format)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "glm-4-flash",  # or appropriate GLM model
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 10
            }

            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                decision = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip().lower()

                # Validate decision
                if decision in ["approve", "reject", "manual"]:
                    return decision
                else:
                    print(f"[WARN] Unexpected GLM response: {decision}, defaulting to manual")
                    return "manual"
            else:
                print(f"[ERROR] GLM API error: {response.status_code} - {response.text}")
                return self._fallback_decision(frontmatter, content, filepath)

        except Exception as e:
            print(f"[ERROR] GLM request failed: {e}")
            return self._fallback_decision(frontmatter, content, filepath)

    def _fallback_decision(self, frontmatter: Dict, content: str, filepath: Path) -> str:
        """
        Fallback decision logic when AI is unavailable.
        Uses simple rule-based matching.
        """
        # Check for dangerous patterns
        dangerous_keywords = [
            "password", "reset password", "verify identity", "urgent action required",
            "account suspended", "click here immediately", "wire transfer", "send money",
            "bitcoin", "cryptocurrency", "lottery", "winner", "inheritance"
        ]

        content_lower = content.lower() + " " + str(frontmatter).lower()

        for keyword in dangerous_keywords:
            if keyword in content_lower:
                return "reject"

        # Auto-approve safe patterns
        if frontmatter.get('type') == 'email':
            sender = frontmatter.get('from', '')
            # Known safe senders (you can customize this)
            safe_domains = ['github.com', 'stackoverflow.com', 'linkedin.com']
            if any(domain in sender.lower() for domain in safe_domains):
                return "approve"

        # Default to manual review
        return "manual"

    def process_needs_action_folder(self) -> Dict[str, int]:
        """
        Process all items in Needs_Action/ folder.

        Returns:
            Dictionary with counts of decisions made
        """
        results = {
            "approved": 0,
            "rejected": 0,
            "manual": 0,
            "errors": 0
        }

        # Get all markdown files
        files = list(self.needs_action.glob("*.md"))

        if not files:
            print("[INFO] No items to process in Needs_Action/")
            return results

        print(f"[INFO] Processing {len(files)} item(s) from Needs_Action/...")

        for filepath in files:
            try:
                # Read file content
                content = filepath.read_text(encoding='utf-8')

                # Parse frontmatter
                frontmatter = self._parse_frontmatter(content)
                body_content = self._extract_body(content)

                # Get AI decision
                print(f"[PROCESSING] {filepath.name}...")
                decision = self._ask_glm_for_decision(frontmatter, body_content, filepath)

                # Move file based on decision
                if decision == "approve":
                    destination = self.pending_approval / filepath.name
                    shutil.move(str(filepath), str(destination))
                    results["approved"] += 1
                    print(f"[APPROVED] {filepath.name}")

                elif decision == "reject":
                    destination = self.rejected / filepath.name
                    shutil.move(str(filepath), str(destination))
                    results["rejected"] += 1
                    print(f"[REJECTED] {filepath.name}")

                else:  # manual
                    destination = self.pending_approval / filepath.name
                    shutil.move(str(filepath), str(destination))
                    results["manual"] += 1
                    print(f"[MANUAL REVIEW] {filepath.name}")

            except Exception as e:
                print(f"[ERROR] Failed to process {filepath.name}: {e}")
                results["errors"] += 1

        return results

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown file."""
        frontmatter = {}

        # Match YAML frontmatter between --- delimiters
        match = re.match(r'^---\n(.*?)\n---\n(.*)', content, re.DOTALL)
        if match:
            yaml_content = match.group(1)
            try:
                import yaml
                frontmatter = yaml.safe_load(yaml_content) or {}
            except:
                pass

        return frontmatter

    def _extract_body(self, content: str) -> str:
        """Extract body content after frontmatter."""
        match = re.match(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return content


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="GLM-powered auto-approval processor"
    )
    parser.add_argument(
        '--vault',
        default=os.getenv('VAULT_PATH', 'AI_Employee_Vault'),
        help='Path to vault'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=120,
        help='Check interval in seconds (default: 120)'
    )

    args = parser.parse_args()

    approver = GLMApprover(args.vault)

    print("=" * 60)
    print("GLM-POWERED AUTO-APPROVAL PROCESSOR")
    print("=" * 60)
    print(f"\nVault: {args.vault}")
    print(f"API: {os.getenv('GLM_API_URL', 'https://api.z.ai/api/paas/v4')}")
    print(f"Mode: {'Once' if args.once else f'Continuous (every {args.interval}s)'}")
    print()

    if args.once:
        # Run once
        results = approver.process_needs_action_folder()
        print()
        print("=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Auto-approved: {results['approved']}")
        print(f"Requires manual review: {results['manual']}")
        print(f"Rejected: {results['rejected']}")
        print(f"Errors: {results['errors']}")
        print("=" * 60)
    else:
        # Run continuous loop
        import time

        while True:
            try:
                print()
                print("=" * 60)
                print("Processing Needs_Action/ with GLM decisions...")
                print("=" * 60)
                print()

                results = approver.process_needs_action_folder()

                print()
                print("=" * 60)
                print("RESULTS")
                print("=" * 60)
                print(f"Auto-approved: {results['approved']}")
                print(f"Requires manual review: {results['manual']}")
                print(f"Rejected: {results['rejected']}")
                print(f"Errors: {results['errors']}")
                print("=" * 60)
                print()
                print(f"[INFO] Waiting {args.interval} seconds until next check...")
                print()

                time.sleep(args.interval)

            except KeyboardInterrupt:
                print("\n[INFO] Stopping GLM auto-approver...")
                break
            except Exception as e:
                print(f"[ERROR] Main loop error: {e}")
                time.sleep(args.interval)


if __name__ == '__main__':
    main()
