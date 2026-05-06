from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import supabase
from auth_utils import get_current_user, require_admin
import uuid

router = APIRouter()


class CouponBody(BaseModel):
    code: str
    type: str  # discount_percent | discount_amount | free_service | loyalty_full
    value: float = 0
    assigned_to_phone: Optional[str] = None
    note: Optional[str] = None


@router.get("")
def list_coupons(admin=Depends(require_admin)):
    res = supabase.table("coupons").select("*").order("created_at", desc=True).execute()
    return res.data


@router.get("/me")
def my_coupons(user=Depends(get_current_user)):
    res = (
        supabase.table("coupons")
        .select("*")
        .eq("assigned_to_phone", user["phone"])
        .eq("used", False)
        .execute()
    )
    return res.data


@router.post("")
def create_coupon(body: CouponBody, admin=Depends(require_admin)):
    existing = supabase.table("coupons").select("id").eq("code", body.code.upper()).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Código ya existe")

    coupon = {
        "id": str(uuid.uuid4()),
        "code": body.code.upper(),
        "type": body.type,
        "value": body.value,
        "assigned_to_phone": body.assigned_to_phone,
        "note": body.note,
        "used": False,
        "is_loyalty": False,
    }
    supabase.table("coupons").insert(coupon).execute()

    # Build whatsapp URL if phone assigned
    whatsapp_url = None
    if body.assigned_to_phone:
        phone = body.assigned_to_phone.replace(r'\D', '')
        msg = f"🎟️ Cupón M&N Clean Car: *{coupon['code']}*\n"
        if body.type == "discount_percent":
            msg += f"Descuento {body.value}%"
        elif body.type == "discount_amount":
            msg += f"Descuento ${body.value} MXN"
        elif body.type == "loyalty_full":
            msg += f"🎁 Limpieza completa por solo ${body.value}"
        else:
            msg += "¡Servicio GRATIS!"
        if body.note:
            msg += f"\n{body.note}"
        import urllib.parse
        whatsapp_url = f"https://wa.me/521{phone}?text={urllib.parse.quote(msg)}"

    return {**coupon, "whatsapp_url": whatsapp_url}


@router.delete("/{coupon_id}")
def delete_coupon(coupon_id: str, admin=Depends(require_admin)):
    supabase.table("coupons").delete().eq("id", coupon_id).execute()
    return {"ok": True}
