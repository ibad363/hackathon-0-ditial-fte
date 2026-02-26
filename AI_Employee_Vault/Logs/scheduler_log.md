# Scheduler Log

Automated actions triggered by scheduler.py

- [2026-02-23 07:00:03] Scheduler started
- [2026-02-23 07:07:21] Scheduler started
- [2026-02-24 00:05:18] Scheduler started
- [2026-02-24 00:05:50] Scheduler started
- [2026-02-24 23:59:24] Scheduler started
- [2026-02-25 00:20:59] Scheduler started
- [2026-02-25 01:38:00] TEST: Verifying Claude CLI subprocess execution
- [2026-02-25 01:38:00] TRIGGERED: Scheduler test - weekly briefing (command: weekly-briefing)
- [2026-02-25 01:38:00] SKIPPED: Scheduler test - weekly briefing (Claude CLI not found - install it first)
- [2026-02-25 01:38:00] TEST: Subprocess test complete
- [2026-02-25 01:38:47] TEST: Verifying Claude CLI subprocess execution
- [2026-02-25 01:38:47] TRIGGERED: Scheduler test - weekly briefing (command: weekly-briefing)
- [2026-02-25 01:38:49] FAILED: Scheduler test - weekly briefing | Error: Error: Claude Code cannot be launched inside another Claude Code session.
Nested sessions share runtime resources and will crash all active sessions.
To bypass this check, unset the CLAUDECODE environ
- [2026-02-25 01:38:49] TEST: Subprocess test complete
- [2026-02-26 07:05:04] Scheduler started
- [2026-02-26 08:00:05] ========================================
- [2026-02-26 08:00:05] MORNING BRIEFING - Starting daily routine
- [2026-02-26 08:00:05] TRIGGERED: Morning email processing (command: process-emails)
- [2026-02-26 08:00:08] FAILED: Morning email processing | Error: error: unknown option '--command'

- [2026-02-26 08:00:08] MORNING BRIEFING - Complete
- [2026-02-26 08:05:08] Checking for approved LinkedIn posts...
- [2026-02-26 08:05:08] LinkedIn approval check complete
