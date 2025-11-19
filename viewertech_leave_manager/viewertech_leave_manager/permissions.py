import frappe

def can_view_dashboard(user=None):
    if not user:
        user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return True
    if "HR Manager" in frappe.get_roles(user):
        return True

    return False