from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from database import settings
from routers import auth, properties, bookings, admin

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
app = FastAPI(title=settings.app_name, version="1.0.0", description="Property rental platform API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.include_router(auth.router)
app.include_router(properties.router)
app.include_router(bookings.router)
app.include_router(admin.router)

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
