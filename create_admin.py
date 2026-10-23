"""Create the first admin account securely."""
from getpass import getpass

from database import SessionLocal
from models import User, UserRole
from security import hash_password

def main():
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password (min 8 characters): ")
    confirm = getpass("Confirm password: ")

    if not name or "@" not in email:
        raise SystemExit("Enter a valid name and email.")

    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters.")

    if password != confirm:
        raise SystemExit("Passwords do not match.")

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise SystemExit("This email is already registered.")

        admin = User(name=name,email=email,hashed_password=hash_password(password),role=UserRole.admin,is_active=True,)
        db.add(admin)
        db.commit()
        print(f"Admin created successfully: {email}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()