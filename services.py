from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import supabase
from auth_utils import get_current_user, require_admin
import uuid

router = APIRouter()


class ServiceBody(BaseModel):
    name: str
    price: float
    includes: List[str]
    active: Optional[bool] = True


@router.get("")
def list_services(user=Depends(get_current_user)):
    res = supabase.table("services").select("*, bookings(id, status)").eq("active", True).execute()
    services = []
    for s in res.data:
        completed = sum(1 for b in (s.get("bookings") or []) if b["status"] == "completed")
        services.append({**{k: v for k, v in s.items() if k != "bookings"}, "completed_count": completed})
    return services


@router.post("")
def create_service(body: ServiceBody, admin=Depends(require_admin)):
    service = {"id": str(uuid.uuid4()), **body.dict()}
    res = supabase.table("services").insert(service).execute()
    return res.data[0]


@router.put("/{service_id}")
def update_service(service_id: str, body: ServiceBody, admin=Depends(require_admin)):
    res = supabase.table("services").update(body.dict()).eq("id", service_id).execute()
    return res.data[0]


@router.delete("/{service_id}")
def delete_service(service_id: str, admin=Depends(require_admin)):
    supabase.table("services").delete().eq("id", service_id).execute()
    return {"ok": True}
