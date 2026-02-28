---
name: slack-manager
description: Monitor Slack channels for important messages, send replies, and manage team communications. Use when you need to interact with Slack.
license: Apache-2.0
---

# Slack Manager

Monitor and interact with Slack for team communication and important messages.

## When to Use This Skill

Use this skill when you need to:
- Check for new Slack messages in channels or DMs
- Send replies or messages to Slack channels
- Monitor for urgent keywords or mentions
- Get channel information and member lists
- Manage team communications asynchronously

## What This Skill Does

Slack Manager provides complete Slack integration:

1. **Message Monitoring** - Watches for new messages in channels and DMs
2. **Urgent Detection** - Flags messages with urgent keywords or mentions
3. **Message Sending** - Sends replies and new messages via MCP
4. **Channel Management** - Gets channel lists and information
5. **User Lookup** - Retrieves user information and profiles

## Quick Start

### Check for New Messages
```
Check Slack for new important messages in #general and #alerts channels
```

### Send a Message
```
Send a message to #general: "Team, the deployment is complete!"
```

### Reply in Thread
```
Reply to the thread in #general about the server issue: "I'm investigating this now."
```

## Workflow

### Monitoring Flow
1. **Slack Watcher** runs in background via PM2
2. Detects new messages with:
   - Bot/user mentions
   - Urgent keywords (urgent, bug, critical, etc.)
   - DMs
3. Creates action files in `AI_Employee_Vault/Needs_Action/`
4. You can read and respond using MCP tools

### Response Flow
1. You identify the need to respond to a Slack message
2. Use `send_message` tool via Slack MCP
3. Specify channel, message text, and optional thread timestamp
4. Message is sent immediately

## Setup

### Prerequisites
1. Create a Slack App at https://api.slack.com/apps
2. Enable OAuth scopes:
   - `channels:history` - Read public channels
   - `groups:history` - Read private channels
   - `im:history` - Read DMs
   - `mpim:history` - Read group DMs
   - `chat:write` - Send messages
   - `users:read` - Get user info
3. Install app to workspace
4. Copy Bot Token (starts with `xoxb-`)

### Environment Variables
```bash
# For Watcher (Python)
export SLACK_BOT_TOKEN="xoxb-your-token-here"
export SLACK_USER_ID="U1234567890"  # Your user ID

# For MCP Server (Node.js - already in mcp.json)
SLACK_BOT_TOKEN="xoxb-your-token-here"
```

### Find Your User ID
1. Open Slack
2. Right-click on your name
3. Select "Copy member ID"
4. Or use: https://api.slack.com/methods/auth.test

## Urgent Keywords

The watcher automatically flags messages containing:
- `urgent`, `asap`, `emergency`, `immediately`
- `deadline`, `due today`, `due tomorrow`
- `invoice`, `payment`, `contract`
- `meeting`, `call`, `appointment`
- `cancel`, `refund`, `complaint`
- `bug`, `critical`, `production`
- `server down`, `error`, `exception`

## MCP Tools

### send_message
Send a message to a channel or DM.

```json
{
  "channel": "#general",
  "text": "Your message here",
  "thread_ts": "1234567890.123456"  // Optional: for threaded replies
}
```

### get_channels
Get list of all public and private channels.

### get_channel_info
Get detailed information about a specific channel.

```json
{
  "channel_id": "C0123456789"
}
```

### get_messages
Get recent messages from a channel.

```json
{
  "channel_id": "C0123456789",
  "limit": "10"
}
```

### get_user_info
Get information about a user.

```json
{
  "user_id": "U1234567890"
}
```

## Examples

### Monitoring Important Channels
```
Monitor these Slack channels for urgent messages:
- #alerts - Production alerts
- #customer-support - Customer issues
- #engineering - Technical discussions
- DMs - Direct messages to me
```

### Sending Status Updates
```
Send a message to #engineering:
"The deployment is complete. All systems are operational.

Changes deployed:
- Feature X: Enabled
- Bug fix Y: Resolved
- Performance improvements: +20%

Please verify and report any issues."
```

### Responding to Mentions
```
I was mentioned in #general about the server issue. Reply:
"@john Thanks for reporting this. I'm investigating the server logs now. Will provide an update in 15 minutes."
```

## Troubleshooting

### "Not in channel" Error
The bot needs to be invited to private channels:
1. Go to channel settings
2. Add the app/bot to the channel

### No Messages Detected
- Check bot token is valid
- Verify bot has required scopes
- Ensure bot is member of the channels
- Check watcher logs: `pm2 logs slack-watcher`

### Messages Not Sending
- Verify `chat:write` scope is enabled
- Check bot is member of target channel
- Ensure channel ID or name is correct
- Check MCP server is running

## File Locations

```
watchers/
└── slack_watcher.py           # Watcher script

mcp-servers/
└── slack-mcp/
    ├── src/
    │   ├── index.ts           # MCP server entry point
    │   ├── slack-client.ts    # Slack API client
    │   └── tools.ts           # MCP tool definitions
    └── dist/                  # Built JavaScript files

.claude/skills/
└── slack-manager/
    └── SKILL.md              # This file

AI_Employee_Vault/
└── Needs_Action/
    └── SLACK_*.md            # Detected messages
```

---

**Next:** Use the Slack watcher to monitor channels and respond to important messages!
