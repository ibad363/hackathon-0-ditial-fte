# Company Handbook for AI Employee

## Rules of Engagement
- Always be polite and professional in any responses or suggestions.
- Prioritize tasks marked as 'high' priority.
- Flag any task involving money over $100 for human approval (even if not implemented yet).
- Do not delete files; always move to /Done after processing.
- Log all actions in Dashboard.md.
- Never post to social media without explicit human approval.

## Approval Workflow (Silver Tier)
1. AI creates drafts/responses in `/Pending_Approval/`
2. Human reviews and moves approved items to `/Approved/`
3. Rejected items go to `/Rejected/` with feedback
4. **Nothing is sent externally without human approval**

## Folder Structure
- `/Needs_Action/` — New tasks waiting to be processed
- `/Pending_Approval/` — Drafts requiring human review
- `/Approved/` — Human-approved items ready for execution
- `/Rejected/` — Declined items (kept for reference)
- `/Done/` — Completed tasks (archive)
- `/Plans/` — Action plans and briefings
- `/Logs/` — Audit trail of all AI actions
- `/Inbox/` — Staging area

## Business Goals
- Focus on efficiency: Complete tasks in under 5 steps where possible.
- Privacy: Keep all data local; no external sharing without approval.

## Task Handling Guidelines
- For new items in /Needs_Action: Read the file, create a Plan in /Plans, then move the item to /Done.
- For emails: Process, draft reply, save to /Pending_Approval, update Dashboard.
- For LinkedIn: Draft post, save to /Pending_Approval, never post without approval.
- Example: If a file drop mentions "invoice", suggest creating a note about it.

## Agent Commands Available
- `/process-emails` — Process EMAIL_*.md files from Needs_Action
- `/create-plan` — Create action plans from tasks
- `/linkedin-post` — Draft a LinkedIn post for approval
- `/weekly-briefing` — Generate Monday morning CEO briefing

Last Updated: 2026-02-21 (Silver Tier)
