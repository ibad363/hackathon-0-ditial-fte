# odoo_mcp.py - Odoo integration for Gold Tier AI Employee
# Uses built-in xmlrpc.client — no extra installs required
# Reads from .env: ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD
#
# Every financial action checks for an approval file in:
#   AI_Employee_Vault/Approved/
# All actions are logged to:
#   AI_Employee_Vault/Logs/Audit/odoo_log.md
# Errors are saved to:
#   AI_Employee_Vault/Error_Queue/

import os
import sys
import xmlrpc.client
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

ODOO_URL      = os.getenv('ODOO_URL', '')
ODOO_DB       = os.getenv('ODOO_DB', '')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', '')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

VAULT_PATH   = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
APPROVED_DIR = VAULT_PATH / 'Approved'
AUDIT_LOG    = VAULT_PATH / 'Logs' / 'Audit' / 'odoo_log.md'
ERROR_QUEUE  = VAULT_PATH / 'Error_Queue'

# Ensure directories exist at import time
APPROVED_DIR.mkdir(parents=True, exist_ok=True)
(VAULT_PATH / 'Logs' / 'Audit').mkdir(parents=True, exist_ok=True)
ERROR_QUEUE.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------

def _log(level: str, message: str):
    """Append a line to the Odoo audit log."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] [{level}] {message}\n"
    with open(AUDIT_LOG, 'a', encoding='utf-8') as f:
        f.write(line)
    print(line, end='')


def _save_error(context: str, error: str):
    """Write an error file to Error_Queue/."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = ERROR_QUEUE / f"odoo_error_{timestamp}.md"
    content = f"# Odoo Error\n\n**Time:** {datetime.now()}\n**Context:** {context}\n**Error:** {error}\n"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    _log('ERROR', f"Error saved to {filename}")


# ---------------------------------------------------------------------------
# Approval guard
# ---------------------------------------------------------------------------

def _check_approval(action_name: str) -> bool:
    """
    Return True if an approval file exists for this action.
    Approval file naming: Approved/odoo_<action_name>.md
    Example: Approved/odoo_create_invoice.md
    """
    approval_file = APPROVED_DIR / f"odoo_{action_name}.md"
    if approval_file.exists():
        _log('INFO', f"Approval found: {approval_file.name}")
        return True
    _log('WARN', f"No approval file for action '{action_name}'. "
                 f"Create: {approval_file} to proceed.")
    print(f"\n[APPROVAL REQUIRED] Create this file to approve the action:\n  {approval_file}\n")
    return False


# ---------------------------------------------------------------------------
# XML-RPC connection factory
# ---------------------------------------------------------------------------

def _get_uid() -> int:
    """Authenticate with Odoo and return the user ID (uid)."""
    if not all([ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD]):
        raise ValueError("Missing Odoo credentials in .env "
                         "(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
    if not uid:
        raise PermissionError("Odoo authentication failed. Check credentials in .env.")
    return uid


def _models():
    """Return an authenticated models proxy."""
    return xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------

def test_connection() -> bool:
    """
    Test the Odoo XML-RPC connection and print server version.
    Returns True on success, False on failure.
    """
    _log('INFO', "Testing Odoo connection...")
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
        version = common.version()
        msg = (f"Connected to Odoo {version.get('server_version', '?')} "
               f"at {ODOO_URL} (db={ODOO_DB})")
        _log('INFO', msg)
        print(f"\n[Odoo] {msg}\n")
        return True
    except Exception as e:
        _save_error('test_connection', str(e))
        return False


def create_invoice(client_name: str, amount: float, description: str,
                   due_date: str) -> dict:
    """
    Create a customer invoice in Odoo.

    Args:
        client_name: Name of the existing Odoo partner/customer.
        amount:      Invoice total (float).
        description: Line item description.
        due_date:    Due date string 'YYYY-MM-DD'.

    Returns:
        dict with keys: success (bool), invoice_id (int), message (str)
    """
    action = 'create_invoice'
    _log('INFO', f"create_invoice called: client={client_name}, amount={amount}, due={due_date}")

    if not _check_approval(action):
        return {'success': False, 'message': 'Approval required. See Approved/ folder.'}

    try:
        uid    = _get_uid()
        models = _models()

        # Find partner by name
        partner_ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.partner', 'search',
            [[['name', 'ilike', client_name]]]
        )
        if not partner_ids:
            msg = f"Partner '{client_name}' not found in Odoo."
            _save_error(action, msg)
            return {'success': False, 'message': msg}

        invoice_vals = {
            'move_type':          'out_invoice',
            'partner_id':         partner_ids[0],
            'invoice_date_due':   due_date,
            'invoice_line_ids': [(0, 0, {
                'name':       description,
                'quantity':   1.0,
                'price_unit': amount,
            })],
        }
        invoice_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'create', [invoice_vals]
        )
        msg = f"Invoice created: id={invoice_id}, client={client_name}, amount={amount}"
        _log('INFO', msg)
        return {'success': True, 'invoice_id': invoice_id, 'message': msg}

    except Exception as e:
        _save_error(action, str(e))
        return {'success': False, 'message': str(e)}


def get_pending_invoices() -> list:
    """
    Return all unpaid customer invoices from Odoo.

    Returns:
        List of dicts: [{ id, name, partner, amount_due, due_date, state }, ...]
    """
    _log('INFO', "Fetching pending invoices...")
    try:
        uid    = _get_uid()
        models = _models()

        ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'search',
            [[['move_type', '=', 'out_invoice'],
              ['payment_state', 'in', ['not_paid', 'partial']]]]
        )
        if not ids:
            _log('INFO', "No pending invoices found.")
            return []

        records = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'read',
            [ids],
            {'fields': ['name', 'partner_id', 'amount_residual', 'invoice_date_due', 'state']}
        )

        invoices = []
        for r in records:
            invoices.append({
                'id':         r['id'],
                'name':       r['name'],
                'partner':    r['partner_id'][1] if r['partner_id'] else 'Unknown',
                'amount_due': r['amount_residual'],
                'due_date':   r['invoice_date_due'],
                'state':      r['state'],
            })

        _log('INFO', f"Found {len(invoices)} pending invoice(s).")
        return invoices

    except Exception as e:
        _save_error('get_pending_invoices', str(e))
        return []


def get_monthly_revenue(year: int = None, month: int = None) -> dict:
    """
    Return total revenue (paid invoices) for the given month.
    Defaults to the current month if year/month not provided.

    Returns:
        dict: { year, month, total_revenue, invoice_count }
    """
    now   = datetime.now()
    year  = year  or now.year
    month = month or now.month
    _log('INFO', f"get_monthly_revenue: {year}-{month:02d}")

    try:
        uid    = _get_uid()
        models = _models()

        date_from = f"{year}-{month:02d}-01"
        # Last day — simple approach: next month day 1 minus 1 day via string math
        if month == 12:
            date_to = f"{year + 1}-01-01"
        else:
            date_to = f"{year}-{month + 1:02d}-01"

        ids = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'search',
            [[['move_type', '=', 'out_invoice'],
              ['payment_state', '=', 'paid'],
              ['invoice_date', '>=', date_from],
              ['invoice_date', '<',  date_to]]]
        )

        total = 0.0
        if ids:
            records = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                'account.move', 'read',
                [ids], {'fields': ['amount_total']}
            )
            total = sum(r['amount_total'] for r in records)

        result = {
            'year':          year,
            'month':         month,
            'total_revenue': round(total, 2),
            'invoice_count': len(ids),
        }
        _log('INFO', f"Monthly revenue {year}-{month:02d}: ${total:.2f} ({len(ids)} invoices)")
        return result

    except Exception as e:
        _save_error('get_monthly_revenue', str(e))
        return {'year': year, 'month': month, 'total_revenue': 0.0, 'invoice_count': 0}


def mark_invoice_paid(invoice_id: int) -> dict:
    """
    Register payment on an Odoo invoice (sets it to paid).

    Args:
        invoice_id: The Odoo account.move integer ID.

    Returns:
        dict: { success (bool), message (str) }
    """
    action = 'mark_invoice_paid'
    _log('INFO', f"mark_invoice_paid called: invoice_id={invoice_id}")

    if not _check_approval(action):
        return {'success': False, 'message': 'Approval required. See Approved/ folder.'}

    try:
        uid    = _get_uid()
        models = _models()

        # Verify invoice exists and is open
        records = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'read',
            [[invoice_id]], {'fields': ['name', 'state', 'payment_state', 'amount_residual']}
        )
        if not records:
            msg = f"Invoice id={invoice_id} not found."
            _save_error(action, msg)
            return {'success': False, 'message': msg}

        rec = records[0]
        if rec['payment_state'] == 'paid':
            msg = f"Invoice {rec['name']} is already paid."
            _log('INFO', msg)
            return {'success': True, 'message': msg}

        # Register payment using the account.payment.register wizard
        ctx = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'account.move', 'action_register_payment',
            [[invoice_id]]
        )
        wizard_model = ctx.get('res_model', 'account.payment.register')
        wizard_ctx   = ctx.get('context', {})

        wizard_id = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            wizard_model, 'create',
            [{}],
            {'context': wizard_ctx}
        )
        models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            wizard_model, 'action_create_payments',
            [[wizard_id]],
            {'context': wizard_ctx}
        )

        msg = f"Invoice {rec['name']} (id={invoice_id}) marked as paid."
        _log('INFO', msg)
        return {'success': True, 'message': msg}

    except Exception as e:
        _save_error(action, str(e))
        return {'success': False, 'message': str(e)}


# ---------------------------------------------------------------------------
# CLI entry point (for quick manual testing)
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    test_connection()
