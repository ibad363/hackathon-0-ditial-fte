# ralph_loop.py - The Ralph autonomous processing loop
#
# run_ralph_loop(max_iterations=20)
#   Each iteration:
#     1. Count Needs_Action files
#     2. Count Error_Queue files
#     3. If both 0 → EXIT cleanly
#     4. Process each file appropriately
#     5. Log iteration to Logs/ralph_log.md
#   Hard stop at max_iterations. Alert human if max reached.

import shutil
from pathlib import Path
from datetime import datetime

from services.audit_logger import log_action
from services.error_handler import process_error_queue, _append_dashboard

VAULT_PATH    = Path('D:/Ibad Coding/hackathon-0-ditial-fte/AI_Employee_Vault')
NEEDS_ACTION  = VAULT_PATH / 'Needs_Action'
ERROR_QUEUE   = VAULT_PATH / 'Error_Queue'
DONE_DIR      = VAULT_PATH / 'Done'
PENDING_DIR   = VAULT_PATH / 'Pending_Approval'
RALPH_LOG     = VAULT_PATH / 'Logs' / 'ralph_log.md'

for _d in [NEEDS_ACTION, ERROR_QUEUE, DONE_DIR, PENDING_DIR]:
    _d.mkdir(parents=True, exist_ok=True)
RALPH_LOG.parent.mkdir(parents=True, exist_ok=True)


def _rlog(msg: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(f"[Ralph] {msg}")
    with open(RALPH_LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def _get_files(directory: Path) -> list:
    """Return sorted list of .md files in directory."""
    return sorted(directory.glob('*.md'))


def _process_needs_action_file(fpath: Path):
    """
    Process a single Needs_Action file.
    Routing logic:
      - If content mentions 'invoice' or 'payment' → move to Pending_Approval
      - If content mentions 'error' or 'fail' → move to Error_Queue
      - Otherwise → move to Done (acknowledged)
    """
    content = fpath.read_text(encoding='utf-8').lower()

    if any(kw in content for kw in ['invoice', 'payment', 'billing', 'financial']):
        dest = PENDING_DIR / fpath.name
        shutil.move(str(fpath), str(dest))
        _rlog(f"  Routed to Pending_Approval: {fpath.name} (financial item)")
        log_action('route_file', 'ralph_loop', fpath.name,
                   {'from': 'Needs_Action', 'to': 'Pending_Approval', 'reason': 'financial'},
                   'success')

    elif any(kw in content for kw in ['error', 'fail', 'exception', 'crash']):
        dest = ERROR_QUEUE / fpath.name
        shutil.move(str(fpath), str(dest))
        _rlog(f"  Routed to Error_Queue: {fpath.name} (error detected)")
        log_action('route_file', 'ralph_loop', fpath.name,
                   {'from': 'Needs_Action', 'to': 'Error_Queue', 'reason': 'error'},
                   'success')

    else:
        dest = DONE_DIR / fpath.name
        shutil.move(str(fpath), str(dest))
        _rlog(f"  Moved to Done: {fpath.name} (acknowledged)")
        log_action('route_file', 'ralph_loop', fpath.name,
                   {'from': 'Needs_Action', 'to': 'Done', 'reason': 'acknowledged'},
                   'success')


def run_ralph_loop(max_iterations: int = 20):
    """
    Main Ralph loop. Processes Needs_Action and Error_Queue until empty
    or max_iterations reached.
    """
    _rlog(f"{'=' * 50}")
    _rlog(f"Ralph Loop started (max iterations: {max_iterations})")
    _rlog(f"{'=' * 50}")

    for iteration in range(1, max_iterations + 1):
        needs_action_files = _get_files(NEEDS_ACTION)
        error_files = _get_files(ERROR_QUEUE)

        na_count = len(needs_action_files)
        eq_count = len(error_files)

        _rlog(f"\n--- Iteration {iteration}/{max_iterations} ---")
        _rlog(f"  Needs_Action: {na_count} files | Error_Queue: {eq_count} files")

        # Exit condition: nothing left to process
        if na_count == 0 and eq_count == 0:
            _rlog(f"All queues empty. Ralph Loop completed in {iteration} iteration(s).")
            log_action('ralph_loop_complete', 'ralph_loop', 'system',
                       {'iterations': iteration, 'reason': 'queues_empty'}, 'success')
            return {'iterations': iteration, 'status': 'complete', 'reason': 'queues_empty'}

        # Process Needs_Action files
        if needs_action_files:
            _rlog(f"  Processing {na_count} Needs_Action file(s)...")
            for fpath in needs_action_files:
                try:
                    _process_needs_action_file(fpath)
                except Exception as e:
                    _rlog(f"  ERROR processing {fpath.name}: {e}")
                    log_action('process_file_error', 'ralph_loop', fpath.name,
                               {'error': str(e)}, 'failure')

        # Process Error Queue
        if error_files:
            _rlog(f"  Processing {eq_count} Error_Queue file(s)...")
            result = process_error_queue()
            _rlog(f"  Error queue result: {result['recovered']} recovered, "
                  f"{result['unrecoverable']} unrecoverable")

    # Max iterations reached — alert human
    _rlog(f"\nMAX ITERATIONS ({max_iterations}) REACHED. Alerting human.")
    _append_dashboard(
        f"ALERT: Ralph Loop hit max {max_iterations} iterations — manual review needed"
    )
    log_action('ralph_loop_max_iterations', 'ralph_loop', 'system',
               {'max_iterations': max_iterations}, 'alert')

    return {'iterations': max_iterations, 'status': 'max_reached', 'reason': 'iteration_limit'}
