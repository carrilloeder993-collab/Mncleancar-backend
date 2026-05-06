from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, services, bookings, coupons, expenses, admin

app = FastAPI(title="MN Clean Car API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(coupons.router, prefix="/coupons", tags=["coupons"])
app.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/")
def root():
    return {"status": "MN Clean Car API running"}
