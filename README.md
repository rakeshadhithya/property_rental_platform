# Property Rental Platform API

REST API for property listings, tenant booking requests, owner decisions, and admin user management.

## Stack
- Python 3.11, FastAPI, SQLAlchemy 2, Alembic
- MySQL 8, JWT (`python-jose`), bcrypt password hashing
- Pydantic v2, `python-multipart`, `aiofiles`, SlowAPI
- pytest + httpx, Docker Compose, python-dotenv / pydantic-settings

## Run with Docker
1. Copy `.env.example` to `.env` and set a strong `SECRET_KEY`.
2. Start services: `docker compose up --build`
3. API docs: http://localhost:8000/docs
4. Health check: http://localhost:8000/health

The API container runs `alembic upgrade head` before starting Uvicorn.

## Run locally
Use Python 3.11 and a reachable MySQL 8 database. Set `DATABASE_URL` in `.env`, then:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

## Tests
```bash
pytest -q
```
Tests use a local SQLite database and reset the schema between tests. Do not point the test suite at production data.

## Roles and security
- Public registration permits `tenant` and `owner`; `admin` must be provisioned securely outside public registration.
- Pass `Authorization: Bearer <token>` for protected routes.
- Owners can manage only their own properties and bookings for those properties.
- Admins can list all bookings and manage user activation; admins can delete any property.
- Passwords are never returned by the API.

## API routes

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/auth/register` | Public | Register tenant or owner |
| POST | `/auth/login` | Public | Get JWT |
| GET | `/properties` | Public | Search available listings with `location`, `min_price`, `max_price` |
| GET | `/properties/{id}` | Public | Property details |
| POST | `/properties` | Owner | Create listing |
| PUT | `/properties/{id}` | Owner (own listing) | Update listing |
| DELETE | `/properties/{id}` | Owner (own listing) / Admin | Delete listing without booking history |
| POST | `/properties/{id}/upload-image` | Owner (own listing) | Upload JPG/PNG, max 2 MiB |
| POST | `/bookings` | Tenant | Request booking |
| GET | `/bookings/my` | Authenticated | Tenant's bookings or owner's property bookings |
| PATCH | `/bookings/{id}/approve` | Owner of property / Admin | Approve requested booking |
| PATCH | `/bookings/{id}/reject` | Owner of property / Admin | Reject requested booking |
| PATCH | `/bookings/{id}/cancel` | Tenant who requested | Cancel requested/approved booking |
| GET | `/bookings` | Admin | List all bookings |
| GET | `/admin/users` | Admin | List users |
| PATCH | `/admin/users/{id}/active?active=false` | Admin | Activate/deactivate user |

## Notes and design decisions
- Booking dates are ISO 8601 datetimes; end must be after start.
- An approved booking marks a property unavailable. Cancelling an approved booking restores availability.
- A tenant cannot have more than one requested/approved booking for the same property.
- Public property search returns available properties only; direct detail lookup can show unavailable properties.
- Image uploads verify MIME type, extension mapping, signature, and size. Files are stored under `UPLOAD_DIR` and served at `/uploads/...`.
- `aiofiles` is included in the requested stack; uploads use bounded reads and local writes to keep size checks simple.
- For production, use HTTPS, rotate secrets, add account/email verification, and consider transactional locking around booking approval to avoid concurrent approvals.
- Admin bootstrap is intentionally not exposed as a public API. Create the first admin through a secure operational script or database procedure.
