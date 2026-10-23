from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from models import UserRole, BookingStatus

class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.tenant

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_active: bool

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class PropertyCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    description: str = Field(min_length=1, max_length=10000)
    location: str = Field(min_length=2, max_length=255)
    price_per_month: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    bedrooms: int = Field(ge=0, le=100)

class PropertyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = Field(default=None, min_length=1, max_length=10000)
    location: str | None = Field(default=None, min_length=2, max_length=255)
    price_per_month: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    bedrooms: int | None = Field(default=None, ge=0, le=100)
    is_available: bool | None = None

class PropertyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    title: str
    description: str
    location: str
    price_per_month: Decimal
    bedrooms: int
    image_path: str | None
    is_available: bool

class BookingCreate(BaseModel):
    property_id: int
    start_date: datetime
    end_date: datetime

    @model_validator(mode="after")
    def valid_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError("end_date must be after start_date")
        return self

class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tenant_id: int
    property_id: int
    start_date: datetime
    end_date: datetime
    status: BookingStatus
    requested_at: datetime
