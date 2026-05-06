from fastapi import APIRouter, Depends
from database import supabase
from auth_utils import require_admin

router = APIRouter()


@router.get("/dashboard")
def dashboard(admin=Depends(require_admin)):
    # Bookings stats
    bookings = supabase.table("bookings").select("status, final_price, service_id").execute().data
    pending = sum(1 for b in bookings if b["status"] == "pending")
    confirmed = sum(1 for b in bookings if b["status"] == "confirmed")
    completed = sum(1 for b in bookings if b["status"] == "completed")
    total_bookings = len(bookings)
    income_total = sum(b["final_price"] for b in bookings if b["status"] == "completed")

    # Expenses
    expenses = supabase.table("expenses").select("cost, services_yield").execute().data
    expense_total = sum(e["cost"] for e in expenses)
    net = income_total - expense_total

    # Services breakdown
    services = supabase.table("services").select("id, name").execute().data
    service_counts = {}
    for b in bookings:
        if b["status"] == "completed":
            service_counts[b["service_id"]] = service_counts.get(b["service_id"], 0) + 1
    services_stats = [{"id": s["id"], "name": s["name"], "completed_count": service_counts.get(s["id"], 0)} for s in services]

    # Inventory / restock alert (every 20 completed services total)
    restock_alert_global = completed > 0 and completed % 20 == 0
    inventory = []
    for e in expenses:
        used = completed  # simplified: all completions consume products
        services_until_restock = max(0, e["services_yield"] - used)
        inventory.append({
            **e,
            "services_until_restock": services_until_restock,
            "needs_restock_alert": services_until_restock <= 5,
        })

    return {
        "pending": pending,
        "confirmed": confirmed,
        "completed": completed,
        "total_bookings": total_bookings,
        "income_total": round(income_total, 2),
        "expense_total": round(expense_total, 2),
        "net": round(net, 2),
        "services": services_stats,
        "inventory": inventory,
        "restock_alert_global": restock_alert_global,
    }
