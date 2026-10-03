from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


EMAIL = "admin@example.com"
PASSWORD = "Admin@12345"
FULL_NAME = "System Administrator"
ROLE = "SUPER_ADMIN"


def create_test_user():
    db = SessionLocal()

    try:
        existing_user = db.execute(
            select(User).where(User.email == EMAIL)
        ).scalar_one_or_none()

        if existing_user:
            print(f"User already exists: {existing_user.email}")
            return

        user = User(
            email=EMAIL,
            password_hash=hash_password(PASSWORD),
            full_name=FULL_NAME,
            role=ROLE,
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print("Test user created successfully.")
        print("ID:", user.id)
        print("Email:", user.email)
        print("Role:", user.role)

    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()