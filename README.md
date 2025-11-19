# **Viewertech Leave Manager**

### *Advanced Leave Automation App for ERPNext*

Viewertech Leave Manager is a custom ERPNext/Frappe application that automates complex HR leave rules, including monthly accrual, mid-year forfeits, December forced leave, company shutdown leave, and year-end carryover limits.

This app is ideal for organizations with strict annual leave policy enforcement requirements.

---

## 🚀 **Features**

### ✅ **1. Monthly Annual Leave Accrual**

* Automatically allocates **2 days** (or configurable value) to all active employees at the end of each month.
* Prevents duplicate allocations.
* Reads values from the **Leave Manager Settings** doctype.

### ✅ **2. Mid-Year Leave Forfeit (End of June)**

* System removes unused leave accumulated from January to June.
* Only applies if enabled in Settings.

### ✅ **3. December Forced Leave**

* Automatically allocates **10 days** forced leave for company closure (configurable).
* Applies to all active employees.
* Logged and tracked.

### ✅ **4. Year-End Carryover Control**

* Employees can carry forward a maximum of **10 days** (configurable).
* Excess leave is deducted automatically.

### ✅ **5. HR Dashboard**

A dedicated dashboard that displays:

* Total monthly leave allocations
* Forfeited leave
* December forced leave
* Carryover statistics
* Employees exceeding limits

Accessible only by **HR Manager** and **System Manager** roles.

### ✅ **6. Role-Based Permissions**

* Only authorized HR users can view or modify settings and dashboards.

---

## 🛠 **Installation**

### **Step 1 — Download the App**

```
bench get-app viewertech_leave_manager https://github.com/viewertech/viewertech_leave_manager.git
```

### **Step 2 — Install on Your Site**

```
bench --site yoursite.com install-app viewertech_leave_manager
```

### **Step 3 — Run Bench**

```
bench restart
```

---

## ⚙ **Configuration**

Go to:

> **ERPNext Desk → Leave Manager Settings**

Available settings:

* Monthly leave allocation (days)
* Carryover limit
* December forced leave days
* Enable/disable each automation rule

---

## 🧩 **Scheduled Jobs**

The application uses the following cron-based jobs:

| Function                       | Frequency        | Purpose                        |
| ------------------------------ | ---------------- | ------------------------------ |
| `monthly_annual_leave_accrual` | Monthly          | Allocate monthly leave         |
| `midyear_forfeit`              | Yearly (June 30) | Forfeit unused leave           |
| `december_forced_leave`        | Yearly (Dec 1)   | Allocate company closure leave |
| `apply_carryover_limit`        | Yearly (Jan 1)   | Enforce carryover restriction  |

---

## 📂 **Directory Structure**

```
viewertech_leave_manager/
├── README.md
├── setup.py
├── viewertech_leave_manager/
│   ├── hooks.py
│   ├── leave_manager.py
│   ├── api.py
│   ├── doctype/
│   │   └── leave_manager_settings/
│   │       ├── leave_manager_settings.json
│   │       └── leave_manager_settings.py
│   └── www/
│       └── leave_dashboard/
│           ├── index.html
│           └── index.js
```

---

## 🤝 **Contributing**

Pull requests are welcome. For major changes, please open an issue first to discuss your proposal.

---

## 📄 **License**

MIT License — you are free to modify and reuse.

---

## 📞 Support

For ERPNext or custom development support:
**Viewertech Africa CC (Namibia & UK)**
Email: **[info@viewertech.africa](mailto:info@viewertech.africa)**

---


