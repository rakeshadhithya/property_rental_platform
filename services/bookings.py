from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Booking, BookingStatus, Property, User, UserRole

ACTIVE_STATUSES = (BookingStatus.requested, BookingStatus.approved)

def request_booking(db: Session, tenant: User, property_id: int, start_date, end_date) -> Booking:
    prop = db.get(Property, property_id)
    if not prop:
        raise HTTPException(404, "Property not found")
    if prop.owner_id == tenant.id:
        raise HTTPException(400, "Owners cannot book their own property")
    if not prop.is_available:
        raise HTTPException(409, "Property is unavailable")
    existing = db.query(Booking).filter(
        Booking.tenant_id == tenant.id,
        Booking.property_id == property_id,
        Booking.status.in_(ACTIVE_STATUSES),
    ).first()
    if existing:
        raise HTTPException(409, "You already have an active booking for this property")
    booking = Booking(tenant_id=tenant.id, property_id=property_id, start_date=start_date, end_date=end_date, status=BookingStatus.requested)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

def decide_booking(db: Session, booking_id: int, owner: User, approve: bool) -> Booking:
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    prop = db.get(Property, booking.property_id)
    if owner.role != UserRole.admin and prop.owner_id != owner.id:
        raise HTTPException(403, "You can only manage bookings for your own properties")
    if booking.status != BookingStatus.requested:
        raise HTTPException(409, "Only requested bookings can be approved or rejected")
    if approve:
        if not prop.is_available:
            raise HTTPException(409, "Property is already unavailable")
        prop.is_available = False
        booking.status = BookingStatus.approved
    else:
        booking.status = BookingStatus.rejected
    db.commit()
    db.refresh(booking)
    return booking
