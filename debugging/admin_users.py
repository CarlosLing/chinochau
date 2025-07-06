#!/usr/bin/env python3
"""
Admin user management script for chinochau.
This script provides utilities to manage admin users.
"""

import sys
from datetime import datetime
from getpass import getpass

from passlib.context import CryptContext

from backend.db import SessionLocal, UserDB, ensure_admin_user_exists

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user():
    """Create a new admin user interactively."""
    print("🔧 Creating new admin user...")

    email = input("Enter admin email: ").strip()
    if not email:
        print("❌ Email is required")
        return False

    full_name = input("Enter full name (optional): ").strip() or None

    password = getpass("Enter password: ")
    if len(password) < 6:
        print("❌ Password must be at least 6 characters")
        return False

    confirm_password = getpass("Confirm password: ")
    if password != confirm_password:
        print("❌ Passwords don't match")
        return False

    db = SessionLocal()
    try:
        # Check if email already exists
        existing_user = db.query(UserDB).filter(UserDB.email == email).first()
        if existing_user:
            print(f"❌ User with email '{email}' already exists")
            return False

        # Create user
        hashed_password = pwd_context.hash(password)
        user = UserDB(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"✅ Created admin user: {email}")
        return True

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def reset_admin_password():
    """Reset password for an admin user."""
    print("🔧 Resetting admin password...")

    email = input("Enter admin email: ").strip()
    if not email:
        print("❌ Email is required")
        return False

    password = getpass("Enter new password: ")
    if len(password) < 6:
        print("❌ Password must be at least 6 characters")
        return False

    confirm_password = getpass("Confirm new password: ")
    if password != confirm_password:
        print("❌ Passwords don't match")
        return False

    db = SessionLocal()
    try:
        user = db.query(UserDB).filter(UserDB.email == email).first()
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False

        # Update password
        user.hashed_password = pwd_context.hash(password)
        db.commit()

        print(f"✅ Password reset for user: {email}")
        return True

    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_users():
    """List all users in the database."""
    print("👥 Listing all users...")

    db = SessionLocal()
    try:
        users = db.query(UserDB).all()

        if not users:
            print("📝 No users found")
            return

        print(f"Found {len(users)} user(s):")
        print("-" * 80)
        print(f"{'ID':<5} {'Email':<30} {'Full Name':<20} {'Active':<8} {'Created'}")
        print("-" * 80)

        for user in users:
            active_status = "Yes" if user.is_active else "No"
            full_name_display = user.full_name if user.full_name else "N/A"
            created_str = (
                user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
            )
            print(
                f"{user.id:<5} {user.email:<30} {full_name_display:<20} {active_status:<8} {created_str}"
            )

    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        db.close()


def ensure_default_admin():
    """Ensure default admin user exists."""
    print("🔧 Ensuring default admin user exists...")
    result = ensure_admin_user_exists()
    if result:
        print("✅ Default admin user created")
    else:
        print("ℹ️  Default admin user already exists or creation skipped")


def main():
    """Main function with menu."""
    print("🛡️  Chinochau Admin User Management")
    print("=" * 40)

    while True:
        print("\nAvailable commands:")
        print("1. List all users")
        print("2. Create new admin user")
        print("3. Reset admin password")
        print("4. Ensure default admin exists")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            list_users()
        elif choice == "2":
            create_admin_user()
        elif choice == "3":
            reset_admin_password()
        elif choice == "4":
            ensure_default_admin()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "list":
            list_users()
        elif command == "create":
            create_admin_user()
        elif command == "reset":
            reset_admin_password()
        elif command == "ensure":
            ensure_default_admin()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: list, create, reset, ensure")
    else:
        main()
