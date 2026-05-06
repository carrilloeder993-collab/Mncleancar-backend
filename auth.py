from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import supabase
from auth_utils import hash_password, verify_password, create_token, get_current_user
import uuid

router = APIRouter()


class RegisterBody(BaseModel):
    phone: str
    password: str
    name: str


class LoginBody(BaseModel):
    phone: str
    password: str


@router.post("/register")
def register(body: RegisterBody):
    existing = supabase.table("users").select("id").eq("phone", body.phone).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="El teléfono ya está registrado")

    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "phone": body.phone,
        "password_hash": hash_password(body.password),
        "name": body.name,
        "role": "client",
    }
    supabase.table("users").insert(user).execute()

    token = create_token(user_id)
    user_safe = {k: v for k, v in user.items() if k != "password_hash"}
    return {"token": token, "user": user_safe}


@router.post("/login")
def login(body: LoginBody):
    res = supabase.table("users").select("*").eq("phone", body.phone).single().execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Teléfono o contraseña incorrectos")

    user = res.data
    if not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Teléfono o contraseña incorrectos")

    token = create_token(user["id"])
    user_safe = {k: v for k, v in user.items() if k != "password_hash"}
    return {"token": token, "user": user_safe}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {k: v for k, v in user.items() if k != "password_hash"}
