#!/usr/bin/env python3
"""
AI-Powered Auto-Approval Processor for AI Employee

Uses Claude AI to intelligently decide which actions to auto-approve
based on Company_Handbook.md rules and context.

Usage:
    python scripts/auto_approver.py --vault AI_Employee_Vault
"""

import json
import os
import sys
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add for HTTP requests to custom API
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import yaml


class AIApprover:
    """AI-powered approval decisions using Claude."""

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

        # Load API key from environment
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

    def _load_handbook_rules(self) -> str:
        """Load Company_Handbook.md to provide context to Claude."""
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

    def _ask_claude_for_decision(self, frontmatter: Dict, content: str, filepath: Path) -> tuple:
        """
        Ask Claude AI to make an approval decision and optionally generate draft.

        Returns:
            (decision, draft_content) tuple where:
            - decision: "approve", "reject", "manual", or "draft"
            - draft_content: AI-generated draft if decision="draft", None otherwise
        """
        if not self.api_key:
            # Fallback to simple rules if no API key
            return (self._fallback_decision(frontmatter, content, filepath), None)

        try:
            import anthropic

            # Determine action type first to decide tokens/temperature
            action_type = frontmatter.get('type', '').lower()
            is_email = action_type == 'email'
            is_social = action_type in ['linkedin_post', 'twitter_post', 'instagram_post', 'facebook_post']
            needs_draft = is_email or is_social

            # Define tokens and temperature BEFORE API call
            max_tokens = 500 if needs_draft else 10
            temperature = 0.7 if needs_draft else 0

            # Support custom base URL for API compatibility
            base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')

            # Check if using custom API endpoint (like z.ai)
            # Custom APIs may have different endpoint structures
            use_custom_api = base_url != 'https://api.anthropic.com' and HAS_REQUESTS

            if use_custom_api:
                # Use direct HTTP request for custom API (z.ai / GLM)
                import requests

                # GLM uses OpenAI-style /chat/completions endpoint
                api_url = base_url.rstrip('/') + '/chat/completions'

                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
            else:
                # Use standard Anthropic SDK
                client = anthropic.Anthropic(api_key=self.api_key, base_url=base_url)

            # Build prompt with context
            if needs_draft:
                prompt = f"""You are an AI assistant that reviews action items and decides how to handle them.

# COMPANY HANDBOOK RULES
{self.handbook_rules[:3000]}

# ACTION TO EVALUATE
Type: {frontmatter.get('type', 'unknown')}
Service: {frontmatter.get('service', 'unknown')}
Priority: {frontmatter.get('priority', 'normal')}
From: {frontmatter.get('from', 'unknown')}
Subject: {frontmatter.get('subject', 'N/A')}

# CONTENT
{content[:2000] if content else '(No content)'}

# YOUR TASK
This is an email reply or social media post request. Your job is to:
1. Check if the content is safe (not spam, not a scam, not dangerous)
2. If safe: Return action="draft" with an AI-generated draft for human review
3. If unsafe (scam, phishing, dangerous): Return action="reject"

Return your decision as a JSON object with these fields:
- action: One of:
  * "draft" - Generate an AI draft for human review (use this for ALL safe emails and social posts)
  * "reject" - Scams, phishing, dangerous requests, spam
- reason: brief explanation of your decision
- draft_content: (REQUIRED if action="draft") AI-generated response

For action="draft":
- Email replies: Professional tone, concise, addresses sender's points, under 200 words
- LinkedIn posts: Professional, 1-3 paragraphs, include 3-5 relevant hashtags
- Twitter posts: Under 280 chars, concise, include 2-3 hashtags
- Instagram posts: Engaging caption style, include 5-10 hashtags
- Facebook posts: Conversational, engaging, include 3-5 hashtags

Respond ONLY with valid JSON (no markdown, no code blocks).
"""
            else:
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
{content[:2000] if content else '(No content)'}

# YOUR TASK
Decide: approve, reject, or manual

Rules:
1. "approve" - Safe routine actions (file ops, known contacts, low-risk tasks)
2. "reject" - Scams, phishing, clearly dangerous actions
3. "manual" - Everything uncertain (social media, payments, new contacts)

Respond with ONLY ONE WORD: approve, reject, or manual
"""

            if use_custom_api:
                # Make HTTP request with custom API (GLM 4.5)
                payload = {
                    'model': 'glm-4',
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'messages': [{'role': 'user', 'content': prompt}]
                }

                response = requests.post(api_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                response_json = response.json()

                # GLM uses OpenAI-style format: choices[0].message.content
                if 'choices' in response_json and len(response_json['choices']) > 0:
                    response_text = response_json['choices'][0]['message']['content'].strip()
                else:
                    response_text = response.text.strip()
            else:
                # Use standard Anthropic SDK
                message = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                response_text = message.content[0].text.strip()

            # Parse response based on whether we expected a draft
            if needs_draft:
                # Parse JSON response
                try:
                    import json
                    # Remove markdown code blocks if present
                    if response_text.startswith('```'):
                        response_text = response_text.split('```', 2)[1].strip()
                        if response_text.startswith('json'):
                            response_text = response_text[4:].strip()

                    result = json.loads(response_text)
                    decision = result.get('action', 'manual').lower()
                    draft_content = result.get('draft_content')

                    if decision not in ["approve", "reject", "manual", "draft"]:
                        print(f"[WARNING] Claude returned unexpected decision: {decision}")
                        return ("manual", None)

                    return (decision, draft_content)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"[WARNING] Failed to parse AI response: {e}")
                    return ("manual", None)
            else:
                decision = response_text.lower()
                if decision in ["approve", "reject", "manual"]:
                    return (decision, None)
                else:
                    print(f"[WARNING] Claude returned unexpected decision: {decision}")
                    return ("manual", None)

        except Exception as e:
            print(f"[WARNING] AI decision failed: {e}, using fallback")
            return (self._fallback_decision(frontmatter, content, filepath), None)

    def _fallback_decision(self, frontmatter: Dict, content: str, filepath: Path) -> str:
        """Fallback rule-based decision if AI is unavailable."""
        action_type = frontmatter.get("type", "") or ""
        service = frontmatter.get("service", "") or ""
        priority = frontmatter.get("priority", "normal") or "normal"
        subject = (frontmatter.get("subject") or "").lower()

        # Handle None content
        content_lower = content.lower() if content else ""

        # REJECT: Payments and scams
        if any(word in subject or word in content_lower for word in ["invoice", "payment", "urgent", "wire transfer", "bitcoin"]):
            return "reject"

        # MANUAL: Social media (always)
        if action_type in ["linkedin_post", "twitter_post", "instagram_post", "facebook_post"]:
            return "manual"

        # MANUAL: High priority
        if priority == "high" or priority == "!!!":
            return "manual"

        # APPROVE: File drops
        if action_type == "file_drop":
            return "approve"

        # MANUAL: Unknown emails
        if action_type == "email" or service == "gmail":
            return "manual"  # Better to review emails

        # APPROVE: Slack/WhatsApp messages (just notifications)
        if action_type in ["slack_message", "whatsapp_message"]:
            return "approve"

        # Default: Manual review
        return "manual"

    def process_needs_action(self) -> Dict[str, int]:
        """
        Process all items in Needs_Action/ and Inbox/ using AI decisions.
        Processes multiple files in parallel for faster processing.

        Returns:
            Dictionary with counts of processed items
        """
        results = {
            "auto_approved": 0,
            "drafted": 0,
            "requires_approval": 0,
            "rejected": 0,
            "errors": 0
        }

        # Process both Needs_Action and Inbox
        files = list(self.needs_action.glob("*.md")) + list((self.vault_path / "Inbox").glob("*.md"))

        if not files:
            return results

        # Process files in parallel using ThreadPoolExecutor
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def process_single_file(filepath):
            """Process a single file and return result status."""
            try:
                # Read file content
                content = filepath.read_text(encoding='utf-8')
                frontmatter = self._extract_frontmatter(filepath)

                # Files with response_status: waiting have interactive checkboxes.
                # For these, we generate an AI draft IN PLACE (don't move the file)
                # so the user can review and check a checkbox in Obsidian.
                if frontmatter.get("response_status") == "waiting":
                    action_type = frontmatter.get('type', '').lower()
                    is_email = action_type == 'email'

                    if is_email and '## AI Suggested Reply' in content:
                        print(f"\n[AI] Generating draft for: {filepath.name}")
                        decision, draft_content = self._ask_claude_for_decision(frontmatter, content, filepath)

                        if draft_content:
                            # Write draft IN PLACE - don't move the file
                            self._write_draft_in_place(filepath, content, frontmatter, draft_content)
                            return ("drafted", filepath.name)
                        else:
                            # Update response_status to ready even without draft
                            self._update_response_status(filepath, content, "ready")
                            return ("drafted", filepath.name)
                    else:
                        # Non-email files: just mark as ready (no AI draft needed)
                        self._update_response_status(filepath, content, "ready")
                        return ("skipped", filepath.name)

                if frontmatter.get("status") == "pending" and frontmatter.get("response_status") != "ready":
                    # Ask AI for decision (returns tuple now)
                    print(f"\n[AI] Analyzing: {filepath.name}")
                    decision, draft_content = self._ask_claude_for_decision(frontmatter, content, filepath)

                    print(f"[AI] Decision: {decision.upper()}")

                    if decision == "approve":
                        self._auto_approve(filepath, frontmatter)
                        return ("auto_approved", filepath.name)

                    elif decision == "reject":
                        # Move to Rejected
                        dest = self.rejected / filepath.name
                        shutil.move(str(filepath), str(dest))
                        return ("rejected", filepath.name)

                    elif decision == "draft":
                        # Generate draft and move to Pending_Approval/
                        if draft_content:
                            self._create_draft_with_content(filepath, frontmatter, draft_content)
                            return ("drafted", filepath.name)
                        else:
                            # Fallback to manual review if draft generation failed
                            dest = self.pending_approval / filepath.name
                            shutil.move(str(filepath), str(dest))
                            return ("requires_approval", filepath.name)

                    else:  # manual
                        # Requires manual approval - move to Pending_Approval
                        dest = self.pending_approval / filepath.name
                        shutil.move(str(filepath), str(dest))
                        return ("requires_approval", filepath.name)

                else:
                    # Skip already processed files
                    return ("skipped", filepath.name)

            except Exception as e:
                print(f"[ERROR] Failed to process {filepath.name}: {e}")
                return ("error", filepath.name)

        # Process up to 5 files in parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_single_file, f): f for f in files}

            for future in as_completed(futures):
                result_type, filename = future.result()
                if result_type in results:
                    results[result_type] += 1

        return results

    def _auto_approve(self, filepath: Path, frontmatter: Dict):
        """Auto-approve an action by moving to Approved/."""
        dest = self.approved / filepath.name

        # Update frontmatter
        frontmatter["status"] = "approved"
        frontmatter["auto_approved"] = True
        frontmatter["approved_at"] = datetime.now().isoformat()
        frontmatter["approved_by"] = "AI (Claude)"

        # Write updated frontmatter
        content = filepath.read_text(encoding='utf-8')
        updated_content = self._update_frontmatter(content, frontmatter)

        # Write to Approved folder
        dest.write_text(updated_content, encoding='utf-8')

        # Delete from Needs_Action
        filepath.unlink()

        print(f"   → Auto-approved and moved to Approved/")

    def _create_draft_with_content(self, filepath: Path, frontmatter: Dict, draft_content: str):
        """Create a draft with AI-generated content and move to Pending_Approval/."""
        # Update frontmatter with draft information
        frontmatter["status"] = "pending_approval"
        frontmatter["response_status"] = "ready"
        frontmatter["draft_content"] = draft_content
        frontmatter["draft_generated_at"] = datetime.now().isoformat()
        frontmatter["draft_generated_by"] = "AI (Claude)"

        # Read original content
        content = filepath.read_text(encoding='utf-8')

        # Inject draft into the ## AI Suggested Reply section if it exists
        if '## AI Suggested Reply' in content:
            content = re.sub(
                r'(## AI Suggested Reply\s*\n)(?:>.*\n?)*',
                r'\1' + draft_content.replace('\\', '\\\\') + '\n\n',
                content
            )

        # Update frontmatter with draft
        updated_content = self._update_frontmatter(content, frontmatter)

        # Write to Pending_Approval folder
        dest = self.pending_approval / filepath.name
        dest.write_text(updated_content, encoding='utf-8')

        # Delete from Needs_Action
        filepath.unlink()

    def _write_draft_in_place(self, filepath: Path, content: str, frontmatter: Dict, draft_content: str):
        """Write AI draft into the file's ## AI Suggested Reply section without moving it."""
        # Replace the AI Suggested Reply placeholder with actual draft
        if '## AI Suggested Reply' in content:
            content = re.sub(
                r'(## AI Suggested Reply\s*\n)(?:>.*\n?)*',
                r'\g<1>' + draft_content + '\n\n',
                content
            )

        # Update response_status in frontmatter
        content = re.sub(
            r'response_status:\s*waiting',
            'response_status: ready',
            content
        )

        filepath.write_text(content, encoding='utf-8')
        print(f"   -> AI draft written in place: {filepath.name}")

    def _update_response_status(self, filepath: Path, content: str, new_status: str):
        """Update response_status field in the file without moving it."""
        updated = re.sub(
            r'response_status:\s*\w+',
            f'response_status: {new_status}',
            content
        )
        if updated != content:
            filepath.write_text(updated, encoding='utf-8')

    def _extract_frontmatter(self, filepath: Path) -> Dict:
        """Extract YAML frontmatter from markdown file, or create metadata for plain text files."""
        content = filepath.read_text(encoding='utf-8')

        if content.startswith("---"):
            # Find end of frontmatter
            try:
                end = content.index("---", 3)
                frontmatter_text = content[3:end]
                import yaml
                return yaml.safe_load(frontmatter_text) or {}
            except (ValueError, yaml.YAMLError):
                pass

        # No frontmatter - create metadata for plain text files
        return {
            "type": "file_drop",
            "status": "pending",
            "created": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
            "original_name": filepath.name,
            "source": "inbox"
        }

    def _update_frontmatter(self, content: str, updates: Dict) -> str:
        """Update YAML frontmatter in markdown content."""
        if content.startswith("---"):
            try:
                end = content.index("---", 3)
                old_frontmatter = content[3:end]
                import yaml
                frontmatter = yaml.safe_load(old_frontmatter) or {}
                frontmatter.update(updates)

                # Build new frontmatter
                new_frontmatter = "---\n"
                for key, value in frontmatter.items():
                    if isinstance(value, (list, dict)):
                        import yaml
                        new_frontmatter += yaml.dump(value, default_flow_style=False)
                    else:
                        new_frontmatter += f"{key}: {value}\n"

                new_frontmatter += "---"

                # Return updated content
                return new_frontmatter + content[end + 3:]
            except (ValueError, yaml.YAMLError):
                pass

        return content


def main():
    """Main entry point."""
    import argparse
    import time

    parser = argparse.ArgumentParser(
        description="AI-powered auto-approval using Claude"
    )
    parser.add_argument("--vault", default="AI_Employee_Vault", help="Path to vault")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("AI-POWERED AUTO-APPROVAL PROCESSOR")
    print("="*60)
    print(f"\nVault: {args.vault}")
    print(f"Rules from: Company_Handbook.md")
    print(f"AI: Claude 3 Haiku")
    print(f"Mode: {'Run once' if args.once else 'Continuous (every 2 minutes)'}\n")

    approver = AIApprover(args.vault)

    def run_once():
        print("[*] Processing Needs_Action/ with AI decisions...\n")

        results = approver.process_needs_action()

        print("\n" + "="*60)
        print("RESULTS")
        print("="*60)
        print(f"Auto-approved: {results['auto_approved']}")
        print(f"AI-drafted: {results['drafted']}")
        print(f"Requires manual review: {results['requires_approval']}")
        print(f"Rejected: {results['rejected']}")
        print(f"Errors: {results['errors']}")
        print("="*60 + "\n")

        return results

    # Run once if requested
    if args.once:
        results = run_once()
        return 0

    # Otherwise run continuously
    try:
        while True:
            results = run_once()
            # Quick check interval - process files as soon as they arrive
            print("[*] Waiting 10 seconds until next check...\n")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[INFO] Auto-approver stopped")
        return 0


if __name__ == "__main__":
    main()
