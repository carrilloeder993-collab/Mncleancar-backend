from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from database import supabase
from auth_utils import get_current_user, require_admin
import uuid

router = APIRouter()

AVAILABLE_HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
MAX_PER_HOUR = 1  # one booking per hour slot


class BookingBody(BaseModel):
    service_id: str
    date: str
    hour: int
    vehicle_type: str
    address: str
    coupon_code: Optional[str] = None


class StatusBody(BaseModel):
    status: str


@router.get("/availability")
def get_availability(date: str = Query(...), user=Depends(get_current_user)):
    res = supabase.table("bookings").select("hour").eq("date", date).in_("status", ["pending", "confirmed"]).execute()
    taken = {b["hour"] for b in res.data}
    slots = [{"hour": h, "available": h not in taken} for h in AVAILABLE_HOURS]
    return {"slots": slots}


@router.get("/me")
def my_bookings(user=Depends(get_current_user)):
    res = (
        supabase.table("bookings")
        .select("*, services(name, price)")
        .eq("user_id", user["id"])
        .order("date", desc=True)
        .execute()
    )
    return _format_bookings(res.data, include_user=False)


@router.get("")
def list_bookings(status: Optional[str] = None, admin=Depends(require_admin)):
    q = supabase.table("bookings").select("*, services(name, price), users(name, phone)")
    if status:
        q = q.eq("status", status)
    res = q.order("date", desc=True).execute()
    return _format_bookings(res.data, include_user=True)


@router.post("")
def create_booking(body: BookingBody, user=Depends(get_current_user)):
    # Check availability
    conflict = (
        supabase.table("bookings")
        .select("id")
        .eq("date", body.date)
        .eq("hour", body.hour)
        .in_("status", ["pending", "confirmed"])
        .execute()
    )
    if conflict.data:
        raise HTTPException(status_code=400, detail="Horario no disponible")

    # Get service
    svc = supabase.table("services").select("price, name").eq("id", body.service_id).single().execute()
    if not svc.data:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")

    final_price = svc.data["price"]
    discount = 0

    # Apply coupon if provided
    if body.coupon_code:
        coupon = (
            supabase.table("coupons")
            .select("*")
            .eq("code", body.coupon_code.upper())
            .eq("used", False)
            .execute()
        )
        if coupon.data:
            c = coupon.data[0]
            if c["type"] == "discount_percent":
                discount = final_price * (c["value"] / 100)
            elif c["type"] == "discount_amount":
                discount = c["value"]
            elif c["type"] in ("free_service", "loyalty_full"):
                discount = final_price
            final_price = max(0, final_price - discount)

    booking = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "service_id": body.service_id,
        "date": body.date,
        "hour": body.hour,
        "vehicle_type": body.vehicle_type,
        "address": body.address,
        "coupon_code": body.coupon_code.upper() if body.coupon_code else None,
        "final_price": final_price,
        "status": "pending",
    }
    supabase.table("bookings").insert(booking).execute()
    return booking


@router.patch("/{booking_id}/status")
def update_status(booking_id: str, body: StatusBody, admin=Depends(require_admin)):
    valid = ["pending", "confirmed", "completed", "rejected"]
    if body.status not in valid:
        raise HTTPException(status_code=400, detail="Estado inválido")

    supabase.table("bookings").update({"status": body.status}).eq("id", booking_id).execute()

    loyalty_coupon = None
    # Check loyalty: every 5 completed bookings → free coupon
    if body.status == "completed":
        booking = supabase.table("bookings").select("user_id").eq("id", booking_id).single().execute()
        if booking.data:
            uid = booking.data["user_id"]
            count = supabase.table("bookings").select("id", count="exact").eq("user_id", uid).eq("status", "completed").execute()
            total = count.count or 0
            if total > 0 and total % 5 == 0:
                code = f"LEALTAD{total}"
                supabase.table("coupons").insert({
                    "id": str(uuid.uuid4()),
                    "code": code,
                    "type": "loyalty_full",
                    "value": 100,
                    "assigned_to_phone": None,
                    "used": False,
                    "is_loyalty": True,
                }).execute()
                loyalty_coupon = code

    return {"ok": True, "loyalty_coupon": loyalty_coupon}


def _format_bookings(data, include_user=False):
    result = []
    for b in data:
        svc = b.get("services") or {}
        usr = b.get("users") or {}
        item = {
            "id": b["id"],
            "date": b["date"],
            "hour": b["hour"],
            "vehicle_type": b["vehicle_type"],
            "address": b["address"],
            "status": b["status"],
            "coupon_code": b.get("coupon_code"),
            "final_price": b.get("final_price", 0),
            "service_name": svc.get("name", ""),
        }
        if include_user:
            item["user_name"] = usr.get("name", "")
            item["user_phone"] = usr.get("phone", "")
        result.append(item)
    return result
