import frappe
from frappe import _

no_cache = 1

def get_context(context):
    if frappe.session.user=='Guest':
        frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)
    context.current_user = frappe.get_doc("User", frappe.session.user)
