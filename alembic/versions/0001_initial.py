"""Initial schema."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    user_role = sa.Enum("tenant", "owner", "admin", name="userrole")
    booking_status = sa.Enum("requested", "approved", "rejected", "cancelled", name="bookingstatus")
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="tenant"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("properties",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("price_per_month", sa.Numeric(10, 2), nullable=False),
        sa.Column("bedrooms", sa.Integer(), nullable=False),
        sa.Column("image_path", sa.String(500)),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_properties_id", "properties", ["id"])
    op.create_index("ix_properties_owner_id", "properties", ["owner_id"])
    op.create_index("ix_properties_location", "properties", ["location"])
    op.create_table("bookings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("status", booking_status, nullable=False, server_default="requested"),
        sa.Column("requested_at", sa.DateTime(), nullable=False))
    op.create_index("ix_bookings_id", "bookings", ["id"])
    op.create_index("ix_bookings_tenant_id", "bookings", ["tenant_id"])
    op.create_index("ix_bookings_property_id", "bookings", ["property_id"])

def downgrade():
    op.drop_table("bookings")
    op.drop_table("properties")
    op.drop_table("users")
