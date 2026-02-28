# Inbox Processor

Process, categorize, and organize incoming items from the Inbox folder into appropriate workflow locations.

## Purpose

The Inbox Processor skill **analyzes** incoming items dropped into the `/Inbox` folder, **classifies** them by urgency and category, and **routes** them to appropriate destinations within the vault. This skill **automates** the initial triage of all incoming information, ensuring nothing gets lost while enabling efficient human review.

## Design Philosophy

- **Triage First**: Every incoming item gets immediate classification
- **Deterministic Routing**: Clear rules govern where each item goes
- **Preserve Context**: Original items are never deleted, only moved
- **Audit Trail**: All processing actions are logged

## Workflow

1. **Scan** the `/Inbox` folder for new items
2. **Analyze** each item's content and metadata
3. **Categorize** by type (email, task, reference, action-required)
4. **Assess** urgency (critical, high, medium, low)
5. **Route** to appropriate destination folder
6. **Log** all actions for audit
7. **Update** Dashboard statistics

## Modularity

This skill can be extended with:
- Custom categorization rules
- Additional destination folders
- Automated responses for certain item types
- Integration with external systems

---

*Inbox Processor Skill v1.0*
