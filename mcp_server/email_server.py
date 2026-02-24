# email_server.py - MCP server for sending emails via Gmail SMTP
# Uses MY_EMAIL and MY_APP_PASSWORD from .env (Gmail App Password)
# Run with: python mcp_server/email_server.py

import sys
import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MY_EMAIL = os.getenv('MY_EMAIL', '')
MY_APP_PASSWORD = os.getenv('MY_APP_PASSWORD', '')

VAULT_PATH = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
LOGS = VAULT_PATH / 'Logs'


# ---------------------------------------------------------------------------
# MCP protocol helpers
# ---------------------------------------------------------------------------

def send_response(response: dict):
    """Write a JSON-RPC response to stdout (MCP protocol)."""
    line = json.dumps(response)
    sys.stdout.write(line + '\n')
    sys.stdout.flush()


def send_error(req_id, code: int, message: str):
    send_response({
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": code, "message": message}
    })


# ---------------------------------------------------------------------------
# Email sending logic
# ---------------------------------------------------------------------------

def send_email(to: str, subject: str, body: str, cc: str = "") -> dict:
    """Send an email via Gmail SMTP using App Password credentials."""
    if not MY_EMAIL or not MY_APP_PASSWORD:
        return {
            "success": False,
            "error": "Missing MY_EMAIL or MY_APP_PASSWORD in .env file."
        }

    try:
        msg = MIMEMultipart()
        msg['From'] = MY_EMAIL
        msg['To'] = to
        msg['Subject'] = subject
        if cc:
            msg['Cc'] = cc

        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        recipients = [to] + ([cc] if cc else [])

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MY_EMAIL, MY_APP_PASSWORD)
            server.sendmail(MY_EMAIL, recipients, msg.as_string())

        log_action(f"Email sent to={to} subject='{subject}'")
        return {"success": True, "to": to, "subject": subject}

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "SMTP authentication failed. Check MY_APP_PASSWORD in .env — must be a Gmail App Password, not your regular password."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def log_action(message: str):
    """Append to email log in the vault."""
    log_file = LOGS / 'email_log.md'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not log_file.exists():
        log_file.write_text("# Email Activity Log\n\n", encoding='utf-8')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"- [{timestamp}] {message}\n")


# ---------------------------------------------------------------------------
# MCP request handlers
# ---------------------------------------------------------------------------

def handle_initialize(req_id, params):
    send_response({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "email-server", "version": "1.0.0"}
        }
    })


def handle_tools_list(req_id):
    send_response({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "tools": [
                {
                    "name": "send_email",
                    "description": "Send an email via Gmail SMTP. Uses MY_EMAIL and MY_APP_PASSWORD from .env.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "to": {
                                "type": "string",
                                "description": "Recipient email address"
                            },
                            "subject": {
                                "type": "string",
                                "description": "Email subject line"
                            },
                            "body": {
                                "type": "string",
                                "description": "Plain text email body"
                            },
                            "cc": {
                                "type": "string",
                                "description": "Optional CC email address"
                            }
                        },
                        "required": ["to", "subject", "body"]
                    }
                }
            ]
        }
    })


def handle_tools_call(req_id, params):
    tool_name = params.get("name")
    args = params.get("arguments", {})

    if tool_name == "send_email":
        to = args.get("to", "").strip()
        subject = args.get("subject", "").strip()
        body = args.get("body", "").strip()
        cc = args.get("cc", "").strip()

        if not to or not subject or not body:
            send_error(req_id, -32602, "Missing required arguments: to, subject, body")
            return

        result = send_email(to, subject, body, cc)

        if result["success"]:
            text = f"Email sent successfully to {result['to']} with subject '{result['subject']}'"
        else:
            text = f"Failed to send email: {result['error']}"

        send_response({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": text}],
                "isError": not result["success"]
            }
        })
    else:
        send_error(req_id, -32601, f"Unknown tool: {tool_name}")


# ---------------------------------------------------------------------------
# Main loop — reads JSON-RPC lines from stdin
# ---------------------------------------------------------------------------

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})

        if method == "initialize":
            handle_initialize(req_id, params)
        elif method == "notifications/initialized":
            pass  # No response needed for notifications
        elif method == "tools/list":
            handle_tools_list(req_id)
        elif method == "tools/call":
            handle_tools_call(req_id, params)
        else:
            if req_id is not None:
                send_error(req_id, -32601, f"Method not found: {method}")


if __name__ == '__main__':
    main()
