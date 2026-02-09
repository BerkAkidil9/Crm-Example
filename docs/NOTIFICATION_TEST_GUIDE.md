# Notification Test Guide

How to test that notifications work correctly.

---

## 1. Instantly triggered notifications (in-app actions)

| Notification | How to test |
|--------------|-------------|
| **New task assigned** | Tasks → Create Task → Assign to a user (other than yourself). Log in as that user and check `/tasks/notifications/`. |
| **Task reassigned** | Edit a task and set "Assigned To" to another user. It should appear in the new assignee's notification list. |
| **Order created** | Orders → Create Order. Organisor + (if order is linked to a lead) the agent receive a notification. |
| **Stock alert** | In ProductsAndStock, create a situation that triggers a stock alert (e.g. product below minimum stock). Organisor receives a notification. |
| **Agent assigned to lead** | Leads → select a lead → Assign Agent. The assigned agent receives a notification. |

---

## 2. Notifications triggered by management commands

These commands **do not run automatically**; run them manually in the terminal for testing.

### Task deadline (1 or 3 days before)

- **Command:** `python manage.py check_task_deadlines`
- **What it does:** For tasks whose **end_date** is tomorrow or 3 days from now and not yet completed (pending/in_progress), sends email + notification to the assigned user.
- **To test:**
  1. Create a task as admin; **end_date** = tomorrow or 3 days from now, status = pending or in_progress.
  2. In terminal: `python manage.py check_task_deadlines`
  3. Check the assigned user's email and `/tasks/notifications/` list.
- **List only, do not send:** `python manage.py check_task_deadlines --dry-run`
- **Different days (e.g. 2 and 5 days):** `python manage.py check_task_deadlines --days 2 5`

### Order day is today (sale completed)

- **Command:** `python manage.py check_order_day`
- **What it does:** For orders whose `order_day` (delivery/completion date) is **today** and not cancelled, sends notification to organisor + agent.
- **To test:**
  1. Set a order's `order_day` to today's date (admin or DB).
  2. Run `python manage.py check_order_day`
  3. Check the relevant organisor and agent notification list.
- **List only:** `python manage.py check_order_day --dry-run`

### Lead has not ordered in 30 days

- **Command:** `python manage.py check_lead_no_order`
- **What it does:** For leads that have an agent and have not placed an order in the last 30 days, sends notification to the agent.
- **To test:**
  1. Assign an agent to a lead; that lead's last order should be older than 30 days (or have no orders and lead created more than 30 days ago).
  2. Run `python manage.py check_lead_no_order`
  3. Check the agent user's notification list.
- **List only:** `python manage.py check_lead_no_order --dry-run`

---

## Quick reference

- Notification list (logged-in user): **`/tasks/notifications/`**
- Unread count is shown in the navbar (via context_processors).

When testing, log in as different users (organisor, agent, assigned user) and verify each role sees their own notifications.
