# WhatsApp Manager - Examples

## Example 1: Daily WhatsApp Check

**Scenario**: Check for overnight client messages every morning at 9 AM.

**Script**: `scripts/daily_whatsapp_scan.py`

```python
#!/usr/bin/env python3
"""
Daily WhatsApp Scan - Check for overnight messages
"""
import sys
import subprocess
from pathlib import Path

def scan_whatsapp():
    """Run WhatsApp watcher and report results."""
    vault_path = Path(__file__).parent.parent.parent
    session_path = vault_path / "whatsapp_session"

    print("Scanning WhatsApp for overnight messages...")

    result = subprocess.run([
        "python",
        "watchers/whatsapp_watcher_simple.py",
        "--vault", str(vault_path),
        "--session", str(session_path)
    ], capture_output=True, text=True, cwd=str(vault_path))

    print(result.stdout)

    if result.returncode == 0:
        # Count created action files
        needs_action = vault_path / "Needs_Action"
        whatsapp_files = list(needs_action.glob("WHATSAPP_*.md"))

        print(f"\nFound {len(whatsapp_files)} WhatsApp messages requiring attention")

        # List recent files
        recent = sorted(whatsapp_files, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        for f in recent:
            print(f"  - {f.name}")
    else:
        print(f"Error: {result.stderr}")
        return False

    return True

if __name__ == "__main__":
    success = scan_whatsapp()
    sys.exit(0 if success else 1)
```

**Usage**:
```bash
# Run manually
python .claude/skills/whatsapp-manager/scripts/daily_whatsapp_scan.py

# Schedule (Windows)
schtasks /create /tn "Daily WhatsApp" /tr "python daily_whatsapp_scan.py" /sc daily /st 09:00

# Schedule (Mac/Linux cron)
0 9 * * * cd /path/to/vault && python .claude/skills/whatsapp-manager/scripts/daily_whatsapp_scan.py
```

**Output**:
```
Scanning WhatsApp for overnight messages...

============================================================
SIMPLE WHATSAPP WATCHER
============================================================
[*] Found 5 messages with keywords

Found 5 WhatsApp messages requiring attention
  - WHATSAPP_12345.md
  - WHATSAPP_67890.md
  ...
```

---

## Example 2: Campaign-Specific Monitoring

**Scenario**: Monitor WhatsApp for responses to a marketing campaign with keyword "launch".

**Add keyword** to `watchers/whatsapp_watcher_simple.py`:

```python
KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'watch',
            'launch', 'promo', 'offer']  # Campaign keywords
```

**Create campaign summary**:

```python
#!/usr/bin/env python3
"""
Campaign Response Aggregator - Collect all WhatsApp mentions
"""
from pathlib import Path
import json
from datetime import datetime, timedelta

def aggregate_campaign_responses(keyword="launch", days=7):
    """Aggregate WhatsApp messages about campaign."""
    vault_path = Path(".")
    needs_action = vault_path / "Needs_Action"

    # Find recent WhatsApp files
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_files = []

    for f in needs_action.glob("WHATSAPP_*.md"):
        if f.stat().st_mtime > cutoff_date.timestamp():
            content = f.read_text()
            if keyword.lower() in content.lower():
                recent_files.append(f)

    # Create summary
    summary = {
        "keyword": keyword,
        "period_days": days,
        "total_mentions": len(recent_files),
        "files": [f.name for f in recent_files],
        "generated_at": datetime.now().isoformat()
    }

    # Save summary
    summary_file = vault_path / f"campaign_{keyword}_summary.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Campaign Summary: {keyword}")
    print(f"Period: Last {days} days")
    print(f"Total mentions: {len(recent_files)}")
    print(f"Saved: {summary_file}")

    return summary

if __name__ == "__main__":
    aggregate_campaign_responses()
```

---

## Example 3: Priority-Based Processing

**Scenario**: Process urgent WhatsApp messages immediately.

**Script**: `scripts/priority_whatsapp_check.py`

```python
#!/usr/bin/env python3
"""
Priority WhatsApp Check - Process urgent messages immediately
"""
import sys
from pathlib import Path
import json

def check_urgent_messages():
    """Check for urgent WhatsApp messages and take action."""
    vault_path = Path(".")
    needs_action = vault_path / "Needs_Action"

    # Find urgent messages
    urgent_files = []

    for f in needs_action.glob("WHATSAPP_*.md"):
        content = f.read_text()

        # Check for urgent keyword in content
        if "urgent" in content.lower() or "asap" in content.lower():
            urgent_files.append(f)

    if not urgent_files:
        print("No urgent messages found")
        return True

    print(f"Found {len(urgent_files)} urgent messages")

    # Process each urgent message
    for f in urgent_files:
        print(f"\nProcessing: {f.name}")

        # Extract details
        lines = f.read_text().split('\n')
        sender = None
        preview = None

        for line in lines:
            if line.startswith("## From:"):
                sender = line.split(":", 1)[1].strip()
            elif line.startswith("## Message Preview"):
                idx = lines.index(line)
                preview = '\n'.join(lines[idx+1:idx+5])

        print(f"  From: {sender}")
        print(f"  Preview: {preview[:100]}...")

        # Create immediate action plan
        plan_file = vault_path / "Plans" / f"URGENT_WHATSAPP_{f.stem}.md"

        plan_content = f"""---
type: urgent_response
priority: critical
source: whatsapp_manager
created: {datetime.now().isoformat()}
---

# Urgent WhatsApp Response Plan

## Message From
{sender}

## Original Message
{preview}

## Action Required
- [ ] Read full message in WhatsApp
- [ ] Assess urgency level
- [ ] Draft immediate response
- [ ] Send response or escalate
- [ ] Document resolution

## Timeline
- **Detection**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Target Response**: Within 30 minutes
- **Escalation**: If no response in 1 hour

---
*Generated by Priority WhatsApp Check*
"""

        plan_file.parent.mkdir(exist_ok=True)
        plan_file.write_text(plan_content)

        print(f"  Created plan: {plan_file.name}")

    return True

if __name__ == "__main__":
    success = check_urgent_messages()
    sys.exit(0 if success else 1)
```

**Usage**:
```bash
# Run every 30 minutes during business hours
python .claude/skills/whatsapp-manager/scripts/priority_whatsapp_check.py
```

---

## Example 4: Weekly WhatsApp Summary

**Scenario**: Generate weekly summary of all WhatsApp activity.

**Script**: `scripts/weekly_whatsapp_summary.py`

```python
#!/usr/bin/env python3
"""
Weekly WhatsApp Summary - Aggregate and analyze WhatsApp activity
"""
from pathlib import Path
from datetime import datetime, timedelta
import json

def generate_weekly_summary():
    """Generate summary of WhatsApp messages from past week."""
    vault_path = Path(".")
    needs_action = vault_path / "Needs_Action"
    briefings = vault_path / "Briefings"

    # Find messages from last 7 days
    cutoff_date = datetime.now() - timedelta(days=7)
    all_messages = []

    for f in needs_action.glob("WHATSAPP_*.md"):
        if f.stat().st_mtime > cutoff_date.timestamp():
            content = f.read_text()

            # Extract metadata
            message_data = {
                "file": f.name,
                "created": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "sender": None,
                "keywords": [],
                "preview": None
            }

            # Parse content
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith("## From:"):
                    message_data["sender"] = line.split(":", 1)[1].strip()
                elif line.startswith("## Detected Keywords"):
                    # Next lines are keywords
                    keywords = []
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            keywords.append(lines[j].strip())
                        else:
                            break
                    message_data["keywords"] = keywords
                elif line.startswith("## Message Preview"):
                    # Next few lines are preview
                    preview_lines = []
                    for j in range(i+1, min(i+10, len(lines))):
                        if lines[j].strip() and not lines[j].startswith("#"):
                            preview_lines.append(lines[j])
                        else:
                            break
                    message_data["preview"] = ' '.join(preview_lines)[:200]

            all_messages.append(message_data)

    # Generate statistics
    keyword_counts = {}
    sender_counts = {}

    for msg in all_messages:
        for kw in msg["keywords"]:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1
        sender = msg.get("sender", "Unknown")
        sender_counts[sender] = sender_counts.get(sender, 0) + 1

    # Create summary
    summary = f"""---
type: weekly_summary
source: whatsapp_manager
period: last 7 days
generated: {datetime.now().isoformat()}
---

# WhatsApp Weekly Summary

## Period
{(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")} to {datetime.now().strftime("%Y-%m-%d")}

## Statistics

### Total Messages
{len(all_messages)} messages with keywords detected

### Keyword Breakdown
"""

    for kw, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
        summary += f"- **{kw}**: {count} messages\n"

    summary += "\n### Top Senders\n"

    for sender, count in sorted(sender_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        summary += f"- {sender}: {count} messages\n"

    summary += f"""
## Messages by Keyword

"""

    # Group messages by keyword
    by_keyword = {}
    for msg in all_messages:
        for kw in msg["keywords"]:
            if kw not in by_keyword:
                by_keyword[kw] = []
            by_keyword[kw].append(msg)

    for kw, messages in sorted(by_keyword.items()):
        summary += f"\n### {kw.upper()} ({len(messages)} messages)\n\n"
        for msg in messages[:5]:  # Show first 5 per keyword
            summary += f"**{msg['sender']}**: {msg.get('preview', 'No preview')[:80]}...\n\n"

    summary += f"""
## Recommendations

### Immediate Actions
- [ ] Review all urgent messages
- [ ] Respond to payment/invoice inquiries
- [ ] Follow up on help requests

### Process Improvements
- [ ] Add auto-response for common queries
- [ ] Create templates for invoice discussions
- [ ] Set up escalation for urgent messages

---
*Generated by Weekly WhatsApp Summary*
"""

    # Save summary
    summary_file = briefings / f"WhatsApp_Weekly_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    summary_file.write_text(summary)

    print(f"Weekly summary saved: {summary_file.name}")
    print(f"Total messages: {len(all_messages)}")
    print(f"Keywords tracked: {len(keyword_counts)}")

    return True

if __name__ == "__main__":
    generate_weekly_summary()
```

**Usage**:
```bash
# Run every Monday morning
python .claude/skills/whatsapp-manager/scripts/weekly_whatsapp_summary.py
```

**Output** (saved to `Briefings/WhatsApp_Weekly_Summary_*.md`):
```markdown
# WhatsApp Weekly Summary

## Period
2026-01-04 to 2026-01-11

## Statistics

### Total Messages
23 messages with keywords detected

### Keyword Breakdown
- **help**: 8 messages
- **payment**: 6 messages
- **urgent**: 5 messages
- **watch**: 4 messages

### Top Senders
- +92 300 2543640: 12 messages
- +92 325 1080019: 6 messages
- SAQIB (KSA): 5 messages
```

---

## Integration Examples

### Example 5: Claude Processing Workflow

**User request**:
```
"Check for any urgent WhatsApp messages and create response plans for each"
```

**Claude's workflow**:
1. Run `priority_whatsapp_check.py`
2. Read generated plan files from `/Plans/`
3. For each urgent message:
   - Assess the situation
   - Draft response options
   - Create approval file in `/Approved/`
4. Present summary to user

### Example 6: Combined Inbox Processing

**User request**:
```
"Process all new items in Needs_Action folder including WhatsApp, email, and files"
```

**Claude's workflow**:
1. Scan `/Needs_Action/` for all `*.md` files
2. Categorize by type:
   - `WHATSAPP_*.md` → WhatsApp Manager
   - `EMAIL_*.md` → Email Manager
   - `FILE_*.md` → File System Manager
3. Process each by priority:
   - Urgent → immediate attention
   - High → today
   - Medium → this week
   - Low → backlog
4. Generate consolidated daily plan

---

## Quick Reference Commands

```bash
# One-time scan
python watchers/whatsapp_watcher_simple.py --vault . --session ../whatsapp_session

# Check for urgent messages
python .claude/skills/whatsapp-manager/scripts/priority_whatsapp_check.py

# Daily scan (9 AM)
python .claude/skills/whatsapp-manager/scripts/daily_whatsapp_scan.py

# Weekly summary
python .claude/skills/whatsapp-manager/scripts/weekly_whatsapp_summary.py

# Campaign tracking
python .claude/skills/whatsapp-manager/scripts/campaign_tracker.py
```
