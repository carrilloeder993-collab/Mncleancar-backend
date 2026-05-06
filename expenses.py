from fastapi import APIRouter, Depends
from pydantic import BaseModel
from database import supabase
from auth_utils import require_admin
import uuid

router = APIRouter()


class ExpenseBody(BaseModel):
    product_name: str
    cost: float
    quantity: str
    services_yield: int
    category: str  # producto | gasolina | otro


@router.get("")
def list_expenses(admin=Depends(require_admin)):
    res = supabase.table("expenses").select("*").order("created_at", desc=True).execute()
    return res.data


@router.post("")
def create_expense(body: ExpenseBody, admin=Depends(require_admin)):
    expense = {"id": str(uuid.uuid4()), **body.dict()}
    res = supabase.table("expenses").insert(expense).execute()
    return res.data[0]


@router.delete("/{expense_id}")
def delete_expense(expense_id: str, admin=Depends(require_admin)):
    supabase.table("expenses").delete().eq("id", expense_id).execute()
    return {"ok": True}
