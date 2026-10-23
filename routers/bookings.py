from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from dependencies import get_current_user, require_role
from models import Booking, BookingStatus, Property, User, UserRole
from schemas import BookingCreate, BookingOut
from services.bookings import request_booking, decide_booking

router = APIRouter(tags=["bookings"])

@router.post("/bookings", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.tenant))):
    return request_booking(db, user, payload.property_id, payload.start_date, payload.end_date)

@router.get("/bookings/my", response_model=list[BookingOut])
def my_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    query = db.query(Booking)
    if user.role == UserRole.tenant:
        query = query.filter(Booking.tenant_id == user.id)
    elif user.role == UserRole.owner:
        query = query.join(Property).filter(Property.owner_id == user.id)
    return query.order_by(Booking.requested_at.desc()).all()

@router.patch("/bookings/{booking_id}/approve", response_model=BookingOut)
def approve_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.owner, UserRole.admin))):
    return decide_booking(db, booking_id, user, True)

@router.patch("/bookings/{booking_id}/reject", response_model=BookingOut)
def reject_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.owner, UserRole.admin))):
    return decide_booking(db, booking_id, user, False)

@router.patch("/bookings/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.tenant))):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    if booking.tenant_id != user.id:
        raise HTTPException(403, "You can only cancel your own bookings")
    if booking.status not in (BookingStatus.requested, BookingStatus.approved):
        raise HTTPException(409, "Only requested or approved bookings can be cancelled")
    was_approved = booking.status == BookingStatus.approved
    booking.status = BookingStatus.cancelled
    if was_approved:
        prop = db.get(Property, booking.property_id)
        prop.is_available = True
    db.commit()
    db.refresh(booking)
    return booking

@router.get("/bookings", response_model=list[BookingOut])
def all_bookings(db: Session = Depends(get_db), user: User = Depends(require_role(UserRole.admin))):
    return db.query(Booking).order_by(Booking.requested_at.desc()).all()
