import os, uuid
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session
from database import get_db, settings
from dependencies import get_current_user, require_role
from models import Property, User, UserRole
from schemas import PropertyCreate, PropertyUpdate, PropertyOut

router = APIRouter(prefix="/properties", tags=["properties"])
ALLOWED_TYPES = {"image/jpeg": ".jpg", "image/png": ".png"}

@router.get("", response_model=list[PropertyOut])
def list_properties(location: str | None = None, min_price: float | None = Query(None, ge=0), max_price: float | None = Query(None, ge=0), db: Session = Depends(get_db)):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(422, "min_price must be less than or equal to max_price")
    query = db.query(Property).filter(Property.is_available.is_(True))
    if location:
        query = query.filter(Property.location.ilike(f"%{location.strip()}%"))
    if min_price is not None:
        query = query.filter(Property.price_per_month >= min_price)
    if max_price is not None:
        query = query.filter(Property.price_per_month <= max_price)
    return query.order_by(Property.id.desc()).all()

@router.get("/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    return prop

@router.post("", response_model=PropertyOut, status_code=201)
def create_property(payload: PropertyCreate, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.owner))):
    prop = Property(owner_id=user.id, **payload.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop

@router.put("/{property_id}", response_model=PropertyOut)
def update_property(property_id: int, payload: PropertyUpdate, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.owner))):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if prop.owner_id != user.id:
        raise HTTPException(403, "You can only update your own properties")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, key, value)
    db.commit()
    db.refresh(prop)
    return prop

@router.delete("/{property_id}", status_code=204)
def delete_property(property_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if user.role != UserRole.admin and not (user.role == UserRole.owner and prop.owner_id == user.id):
        raise HTTPException(403, "Only the owner or an admin can delete this property")
    if prop.bookings:
        raise HTTPException(409, "Cannot delete a property with booking history")
    db.delete(prop)
    db.commit()
    return None

@router.post("/{property_id}/upload-image", response_model=PropertyOut)
async def upload_image(property_id: int, image: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.owner))):
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if prop.owner_id != user.id:
        raise HTTPException(403, "You can only upload images for your own properties")
    suffix = ALLOWED_TYPES.get(image.content_type or "")
    if not suffix:
        raise HTTPException(415, "Only JPG and PNG images are accepted")
    content = await image.read(settings.max_upload_size + 1)
    if len(content) > settings.max_upload_size:
        raise HTTPException(413, "Image must be 2 MB or smaller")
    # Check file signatures as content-type headers can be spoofed.
    valid = (suffix == ".jpg" and content.startswith(b"\xff\xd8\xff")) or (suffix == ".png" and content.startswith(b"\x89PNG\r\n\x1a\n"))
    if not valid:
        raise HTTPException(415, "File content does not match JPG/PNG format")
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    (upload_dir / filename).write_bytes(content)
    prop.image_path = f"/uploads/{filename}"
    db.commit()
    db.refresh(prop)
    return prop
