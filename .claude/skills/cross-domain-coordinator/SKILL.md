---
name: cross-domain-coordinator
description: Coordinate tasks across Personal and Business domains. Identifies cross-domain dependencies, routes items to appropriate domain folders, and provides unified insights across personal and business contexts.
license: MIT
---

# Cross-Domain Coordinator Skill

## Overview

The Cross-Domain Coordinator manages the intersection of Personal and Business domains in your AI Employee system. It classifies items into domains, identifies cross-domain dependencies, and provides unified insights.

## Features

### 1. Domain Classification
- **Personal Domain**: Health, family, personal finance, education, hobbies
- **Business Domain**: Clients, invoices, projects, social media, accounting
- **Shared Domain**: Items that apply to both (urgent tasks, reminders, scheduling)

### 2. Cross-Domain Routing
Automatically routes items to domain-specific folders:
- `/Needs_Action/Personal/` - Personal tasks and events
- `/Needs_Action/Business/` - Business tasks and events
- `/Needs_Action/Shared/` - Items affecting both domains

### 3. Dependency Detection
Identifies when items in one domain depend on items in another:
- Business travel requires personal calendar availability
- Client meetings conflict with personal appointments
- Business expenses affect personal budget

### 4. Unified Dashboard Updates
Provides cross-domain insights in the Dashboard:
- Personal vs Business task balance
- Cross-domain conflicts detected
- Unified priority recommendations

## Usage

### Classify and Route Items

```python
from watchers.domain_classifier import classify_domain, classify_and_route

# Classify an email
domain = classify_domain(
    subject="Invoice #1234 from Acme Corp",
    content="Please find attached invoice for services rendered",
    sender="billing@acmecorp.com",
    source="gmail"
)
# Returns: Domain.BUSINESS

# Classify a personal appointment
domain = classify_domain(
    subject="Doctor Appointment Tomorrow",
    content="Reminder: Your appointment with Dr. Smith at 10 AM",
    sender="clinic@healthcare.com",
    source="gmail"
)
# Returns: Domain.PERSONAL

# Route a file to appropriate domain folder
domain, new_path = classify_and_route(
    filepath="AI_Employee_Vault/Needs_Action/EMAIL_123.md",
    vault_path="AI_Employee_Vault",
    subject="Meeting with client",
    content="Project status update",
    sender="client@company.com",
    source="gmail"
)
```

### Detect Cross-Domain Conflicts

The coordinator automatically detects:
- Time conflicts between business meetings and personal appointments
- Resource conflicts (budget allocation, equipment use)
- Priority conflicts (urgent tasks in both domains)

### Generate Cross-Domain Insights

The coordinator provides unified insights:
- Task distribution by domain
- Cross-domain dependency graph
- Conflict resolution recommendations
- Work-life balance metrics

## Domain Classification Rules

### Business Domain
- Keywords: invoice, payment, client, customer, contract, meeting, project, social media, accounting
- Senders: Company email domains (@*.com excluding common personal domains)
- Sources: Xero, Odoo, LinkedIn, Twitter, Facebook, Instagram

### Personal Domain
- Keywords: doctor, family, shopping, home, insurance, bank, school, vacation, gym
- Senders: @gmail.com, @yahoo.com, @outlook.com, @hotmail.com, @icloud.com
- Sources: Personal contacts, family accounts

### Shared Domain
- Keywords: urgent, asap, important, reminder, schedule, document
- Items with equal business/personal scores
- Items explicitly tagged as cross-domain

## Integration with Watchers

All watchers can use domain classification:

```python
# In any watcher
from watchers.domain_classifier import classify_domain, get_domain_folder

class GmailWatcher(BaseWatcher):
    def create_action_file(self, message):
        # Extract details
        subject = message['subject']
        content = message['snippet']
        sender = message['from']

        # Classify domain
        domain = classify_domain(subject, content, sender, "gmail")

        # Get domain-specific folder
        domain_folder = get_domain_folder(self.vault_path, domain)

        # Create file in domain folder
        filepath = Path(domain_folder) / f"EMAIL_{message['id']}.md"
        filepath.write_text(content)
```

## Dashboard Integration

The coordinator updates the Dashboard with cross-domain metrics:

```markdown
## Cross-Domain Overview

### Task Distribution
- Personal: 12 tasks (3 urgent)
- Business: 28 tasks (8 urgent)
- Shared: 5 tasks (2 urgent)

### Conflicts Detected
- [ ] Tuesday 2 PM: Client meeting vs Doctor appointment
- [ ] Budget allocation: Business expense vs Personal savings goal

### Recommendations
- Reschedule doctor appointment to Wednesday morning
- Allocate 15% of revenue to personal savings
- Block Friday afternoons for personal time
```

## Files

- `watchers/domain_classifier.py` - Core classification logic
- `.claude/skills/cross-domain-coordinator/` - This skill
- Integration points in all watchers

## Configuration

No configuration required. The classifier uses keyword matching and email patterns.

For custom domain rules, edit the keyword lists in `domain_classifier.py`:

```python
BUSINESS_KEYWORDS = ["your", "custom", "keywords"]
PERSONAL_KEYWORDS = ["your", "custom", "keywords"]
```

## Testing

Test the classifier:

```bash
python -m watchers.domain_classifier
```

This runs test cases and displays classification results.

## Gold Tier Feature

This skill completes the **Cross-Domain Integration** requirement for Gold Tier:
- ✅ Full cross-domain integration (Personal + Business)
- ✅ Domain-specific folder structure
- ✅ Dependency detection
- ✅ Unified insights
