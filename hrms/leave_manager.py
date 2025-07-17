from collections import defaultdict
from datetime import date
from typing import Dict, Optional

from hrms.schemas import LeaveApplyRequest


class LeaveManager:
    DEFAULT_BALANCE = 20

    def __init__(self):
        # history -> list[str] (ISO date strings)
        self.employee_leaves: Dict[str, Dict] = defaultdict(self._default_record)

    @staticmethod
    def _default_record():
        return {"balance": LeaveManager.DEFAULT_BALANCE, "history": []}

    def init_employee(self, employee_id: str, starting_balance: Optional[int] = None) -> None:
        """
        Explicitly create (or reset) a leave record for an employee.
        Call this from your employee onboarding flow if you want to be explicit.
        """
        rec = self.employee_leaves[employee_id]  # triggers default creation if missing
        if starting_balance is not None:
            rec["balance"] = starting_balance

    def get_leave_balance(self, employee_id: str) -> str:
        # Indexing triggers default creation, so new employees auto‑init here.
        rec = self.employee_leaves[employee_id]
        return f"{employee_id} has {rec['balance']} leave day(s) remaining."

    def apply_leave(self, req: LeaveApplyRequest) -> str:
        rec = self.employee_leaves[req.emp_id]  # auto‑init if missing
        leave_dates = [d.isoformat() for d in req.leave_dates]
        requested = len(leave_dates)
        if rec["balance"] < requested:
            return (
                f"Insufficient leave balance: requested {requested}, "
                f"available {rec['balance']}."
            )
        rec["balance"] -= requested
        rec["history"].extend(leave_dates)
        return (
            f"Leave applied for {requested} day(s). Remaining balance: "
            f"{rec['balance']}."
        )

    def get_leave_history(self, employee_id: str) -> str:
        rec = self.employee_leaves[employee_id]  # auto‑init if missing
        if not rec["history"]:
            return f"No leave history for {employee_id}."
        # Parse ISO strings to dates for nice formatting
        dates = [
            date.fromisoformat(d).strftime("%B %d, %Y")
            for d in rec["history"]
        ]
        return f"Leave history for {employee_id}: {', '.join(dates)}."


if __name__ == "__main__":
    lm = LeaveManager()
    # Demonstrate auto-init
    print(lm.get_leave_balance("E004"))        # auto-creates record w/ default balance
    print(lm.apply_leave(LeaveApplyRequest(emp_id="E004", leave_dates=[])))
    print(lm.get_leave_history("E004"))
