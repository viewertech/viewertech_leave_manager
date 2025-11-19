### --- viewertech_leave_manager/viewertech_leave_manager/www/leave_dashboard/leave_dashboard.py ---
import frappe
from frappe import _

def get_context(context):
    # This page is meant to be accessed by HR users from the Desk URL: /leave-dashboard
    context.title = "Leave Manager Dashboard"
    # Stats are fetched via API; keep minimal server-side context
    return context
