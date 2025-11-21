### --- viewertech_leave_manager/viewertech_leave_manager/leave_manager.py (Updated - settings + robust balances) ---
import frappe
from frappe.utils import nowdate, getdate, get_last_day

LEAVE_TYPE = "Annual Leave"


def get_settings():
    try:
        return frappe.get_single("Leave Manager Settings")
    except Exception:
        # fallback defaults
        class _S: pass
        s = _S()
        s.monthly_allocation = 2.0
        s.carryover_limit = 10.0
        s.december_forced_days = 10.0
        s.enable_monthly = True
        s.enable_midyear_forfeit = True
        s.enable_december_forced = True
        s.enable_carryover = True
        return s


def _get_active_employees():
    return frappe.get_all("Employee", filters={"status": "Active"}, fields=["name"])


def _current_balance(employee, leave_type=LEAVE_TYPE):
    """Return the latest leave balance for an employee and leave type.
    Uses Leave Ledger Entry table to retrieve the most recent balance."""
    res = frappe.db.sql(
        """
        SELECT leave_balance
        FROM `tabLeave Ledger Entry`
        WHERE employee=%s AND leave_type=%s
        ORDER BY creation DESC LIMIT 1
        """,
        (employee, leave_type), as_list=1
    )
    if res and res[0] and res[0][0] is not None:
        return float(res[0][0])
    return 0.0


def monthly_annual_leave_accrual():
    settings = get_settings()
    if not getattr(settings, 'enable_monthly', True):
        frappe.logger().info("Monthly allocation disabled in settings")
        return

    today = getdate(nowdate())
    from_date = today.replace(day=1)
    to_date = get_last_day(today)
    alloc_days = float(getattr(settings, 'monthly_allocation', 2))

    for emp in _get_active_employees():
        # Check if allocation already exists for this employee and period
        existing = frappe.get_all(
            "Leave Allocation",
            filters={
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": from_date,
                "to_date": to_date,
            },
            fields=["name", "new_leaves_allocated"]
        )

        if existing:
            # Increment existing allocation
            doc = frappe.get_doc("Leave Allocation", existing[0].name)
            doc.new_leaves_allocated = (doc.new_leaves_allocated or 0) + alloc_days
            doc.note = "Monthly automatic allocation updated"
            doc.save(ignore_permissions=True)
            try:
                if doc.docstatus == 0:
                    doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit updated allocation for {emp.name}: {e}")
        else:
            # Create a new allocation if none exists
            doc = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": from_date,
                "to_date": to_date,
                "new_leaves_allocated": alloc_days,
                "note": "Monthly automatic allocation",
            })
            doc.insert(ignore_permissions=True)
            try:
                doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit allocation for {emp.name}: {e}")




def forfeit_first_half_year_balance():
    settings = get_settings()
    if not getattr(settings, 'enable_midyear_forfeit', True):
        frappe.logger().info("Mid-year forfeit disabled in settings")
        return

    year = getdate(nowdate()).year
    start = f"{year}-01-01"
    mid = f"{year}-06-30"

    for emp in _get_active_employees():
        allocated = frappe.db.sql(
            """SELECT COALESCE(SUM(new_leaves_allocated),0) FROM `tabLeave Allocation`
               WHERE employee=%s AND leave_type=%s
               AND from_date >= %s AND to_date <= %s""",
            (emp.name, LEAVE_TYPE, start, mid), as_list=1
        )[0][0]

        taken = frappe.db.sql(
            """SELECT COALESCE(SUM(total_leave_days),0) FROM `tabLeave Application`
               WHERE employee=%s AND leave_type=%s
               AND from_date >= %s AND to_date <= %s
               AND status='Approved'""",
            (emp.name, LEAVE_TYPE, start, mid), as_list=1
        )[0][0]

        balance = float(allocated or 0) - float(taken or 0)
        if balance <= 0:
            continue

        # Check for existing allocation
        existing = frappe.get_all(
            "Leave Allocation",
            filters={
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": mid,
                "to_date": mid,
            },
            fields=["name", "new_leaves_allocated"]
        )

        if existing:
            doc = frappe.get_doc("Leave Allocation", existing[0].name)
            doc.new_leaves_allocated = (doc.new_leaves_allocated or 0) - balance
            doc.note = "Mid-year forfeit updated"
            doc.save(ignore_permissions=True)
            try:
                if doc.docstatus == 0:
                    doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit updated mid-year forfeit for {emp.name}: {e}")
        else:
            doc = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": mid,
                "to_date": mid,
                "new_leaves_allocated": -balance,
                "note": "Forfeit unused Jan-Jun annual leave",
            })
            doc.insert(ignore_permissions=True)
            try:
                doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit mid-year forfeit for {emp.name}: {e}")


def enforce_december_forced_leave():
    settings = get_settings()
    if not getattr(settings, 'enable_december_forced', True):
        frappe.logger().info("December forced leave disabled in settings")
        return

    year = getdate(nowdate()).year
    start = f"{year}-12-01"
    end = f"{year}-12-31"
    forced_days = float(getattr(settings, 'december_forced_days', 10))

    for emp in _get_active_employees():
        existing = frappe.get_all(
            "Leave Allocation",
            filters={
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": start,
                "to_date": end,
            },
            fields=["name", "new_leaves_allocated"]
        )

        if existing:
            doc = frappe.get_doc("Leave Allocation", existing[0].name)
            doc.new_leaves_allocated = max(forced_days, doc.new_leaves_allocated)
            doc.note = "December forced leave updated"
            doc.save(ignore_permissions=True)
            try:
                if doc.docstatus == 0:
                    doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit updated December forced leave for {emp.name}: {e}")
        else:
            doc = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": start,
                "to_date": end,
                "new_leaves_allocated": forced_days,
                "note": "Mandatory company closure - December",
            })
            doc.insert(ignore_permissions=True)
            try:
                doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit December forced leave for {emp.name}: {e}")


def enforce_carryover_limit():
    settings = get_settings()
    if not getattr(settings, 'enable_carryover', True):
        frappe.logger().info("Carryover enforcement disabled in settings")
        return

    limit = float(getattr(settings, 'carryover_limit', 10.0))
    today = nowdate()

    for emp in _get_active_employees():
        balance = _current_balance(emp.name)
        if balance <= limit:
            continue

        excess = balance - limit
        # Update an existing allocation for today if exists
        existing = frappe.get_all(
            "Leave Allocation",
            filters={
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": today,
                "to_date": today,
            },
            fields=["name", "new_leaves_allocated"]
        )

        if existing:
            doc = frappe.get_doc("Leave Allocation", existing[0].name)
            doc.new_leaves_allocated = (doc.new_leaves_allocated or 0) - excess
            doc.note = "Year-end carryover limit enforcement updated"
            doc.save(ignore_permissions=True)
            try:
                if doc.docstatus == 0:
                    doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit updated carryover deduction for {emp.name}: {e}")
        else:
            doc = frappe.get_doc({
                "doctype": "Leave Allocation",
                "employee": emp.name,
                "leave_type": LEAVE_TYPE,
                "from_date": today,
                "to_date": today,
                "new_leaves_allocated": -excess,
                "note": "Year-end carryover limit enforcement",
            })
            doc.insert(ignore_permissions=True)
            try:
                doc.submit()
            except Exception as e:
                frappe.log_error(f"Failed to submit carryover deduction for {emp.name}: {e}")
