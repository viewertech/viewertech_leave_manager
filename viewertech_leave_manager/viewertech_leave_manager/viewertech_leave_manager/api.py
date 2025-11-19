import frappe
from frappe.utils import nowdate, getdate

@frappe.whitelist()
def dashboard_stats():
    """Return JSON with top-level stats for HR dashboard."""
    year = getdate(nowdate()).year
    employees = frappe.get_all("Employee", filters={"status":"Active"}, fields=["name","employee_name"])[:]
    total_employees = len(employees)

    # total allocated this year
    allocated = frappe.db.sql("SELECT COALESCE(SUM(new_leaves_allocated),0) FROM `tabLeave Allocation` WHERE leave_type=%s AND YEAR(from_date)=%s", ("Annual Leave", year))[0][0] or 0
    taken = frappe.db.sql("SELECT COALESCE(SUM(total_leave_days),0) FROM `tabLeave Application` WHERE leave_type=%s AND YEAR(from_date)=%s AND status='Approved'", ("Annual Leave", year))[0][0] or 0

    # employees with > carryover limit
    limit = float(frappe.get_single("Leave Manager Settings").carryover_limit or 10)
    rows = frappe.db.sql("SELECT employee, MAX(leave_balance) as bal FROM `tabLeave Ledger Entry` WHERE leave_type=%s GROUP BY employee HAVING MAX(leave_balance) > %s", ("Annual Leave", limit), as_dict=1)

    return {
        "total_employees": total_employees,
        "allocated_this_year": float(allocated),
        "taken_this_year": float(taken),
        "employees_over_carryover": rows,
    }