---
name: calendar-manager
description: Monitor Google Calendar for upcoming events and create action files for meeting preparation.
license: Apache-2.0
---

# Calendar Manager

Monitor Google Calendar for upcoming events requiring preparation.

## Purpose

**Detect and Prepare** for upcoming calendar events automatically. The Calendar Manager **monitors** your Google Calendar for upcoming meetings, **creating** preparation files with agendas and checklists.

## Design Principles

1. **API-Based Monitoring**: Uses Google Calendar API for reliable access
2. **OAuth2 Authentication**: Secure token-based authentication
3. **Time-Based Filtering**: Prioritizes events within 24 hours
4. **Keyword Detection**: Identifies meeting types for preparation

## Usage

```bash
# First-time setup
python -m watchers.calendar_watcher --vault . --credentials client_secret.json --once

# Run continuously (every 60 seconds)
python -m watchers.calendar_watcher --vault . --credentials client_secret.json
```

## Event Filtering

- **High Priority**: Events < 24 hours away
- **Meeting Prep**: Events with "meeting", "call", "interview"
- **Keyword Flagging**: Events with specific keywords

## Output Format

`Needs_Action/EVENT_[id]_[timestamp].md` containing:
- Event title, date/time, attendees
- Meeting preparation checklist
- Agenda suggestions

## Integration Points

- **Daily Review**: Daily agenda summaries
- **Planning Agent**: Meeting preparation workflows
