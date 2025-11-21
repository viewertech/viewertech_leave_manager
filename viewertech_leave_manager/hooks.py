### --- viewertech_leave_manager/hooks.py ---
app_name = "viewertech_leave_manager"
app_title = "Viewertech Leave Manager"
app_publisher = "Viewertech"
app_description = "Automates monthly accrual, mid-year forfeits, December forced leave and year-end carryover limit."
app_icon = "octicon octicon-check"
app_color = "green"
app_email = "admin@viewertech.net"
app_license = "MIT"

app_include_js = "/assets/viewertech_leave_manager/js/leave_dashboard.min.js"
app_include_css = "/assets/viewertech_leave_manager/css/leave_dashboard.min.css"

# Scheduler Events
scheduler_events = {
"cron": {
# run at 23:50 on last day of month -> monthly accrual
"50 23 L * *": [
"viewertech_leave_manager.leave_manager.monthly_annual_leave_accrual"
],
# run 00:05 on 1 July -> forfeit first half
"5 0 1 7 *": [
"viewertech_leave_manager.leave_manager.forfeit_first_half_year_balance"
],
# run 00:05 on 1 Dec -> create forced leave applications
"5 0 1 12 *": [
"viewertech_leave_manager.leave_manager.enforce_december_forced_leave"
],
# run 00:10 on 1 Jan -> enforce carryover limit
"10 0 1 1 *": [
"viewertech_leave_manager.leave_manager.enforce_carryover_limit"
],
}
}


# Include in fixtures if you add DocTypes or Settings
fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            ["name", "in", [
                "Leave Manager Settings-monthly_allocation",
                "Leave Manager Settings-carryover_limit",
                "Leave Manager Settings-december_forced_days",
                "Leave Manager Settings-enable_monthly",
                "Leave Manager Settings-enable_midyear_forfeit",
                "Leave Manager Settings-enable_december_forced",
                "Leave Manager Settings-enable_carryover"
            ]]
        ]
    },
    {
        "dt": "Custom DocType",
        "filters": [
            ["name", "in", ["Leave Manager Settings"]]
        ]
    }
]

has_permission = {
    "leave_dashboard": "viewertech_leave_manager.viewertech_leave_manager.permissions.can_view_dashboard"
}