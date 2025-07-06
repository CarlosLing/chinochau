#!/usr/bin/env python3
"""
Debug script to inspect users in the flashcards.db database.
This script will show all users and their information.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = "flashcards.db"


def check_database_exists():
    """Check if the database file exists."""
    if not Path(DB_PATH).exists():
        print(f"❌ Database file '{DB_PATH}' does not exist!")
        return False
    return True


def check_users_table():
    """Check if the users table exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        result = cursor.fetchone()
        if not result:
            print("❌ Users table does not exist!")
            return False
        else:
            print("✅ Users table exists")
            return True
    except Exception as e:
        print(f"❌ Error checking users table: {e}")
        return False
    finally:
        conn.close()


def list_all_users():
    """List all users in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, email, full_name, is_active, created_at FROM users")
        users = cursor.fetchall()

        if not users:
            print("📝 No users found in the database")
            return []

        print(f"👥 Found {len(users)} user(s):")
        print("-" * 80)
        print(f"{'ID':<5} {'Email':<30} {'Full Name':<20} {'Active':<8} {'Created'}")
        print("-" * 80)

        for user in users:
            user_id, email, full_name, is_active, created_at = user
            active_status = "Yes" if is_active else "No"
            full_name_display = full_name if full_name else "N/A"
            print(
                f"{user_id:<5} {email:<30} {full_name_display:<20} {active_status:<8} {created_at}"
            )

        return users
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []
    finally:
        conn.close()


def check_flashcards_ownership():
    """Check flashcard ownership status."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if flashcards table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='flashcards'"
        )
        if not cursor.fetchone():
            print("📝 No flashcards table found")
            return

        # Check total flashcards
        cursor.execute("SELECT COUNT(*) FROM flashcards")
        total_flashcards = cursor.fetchone()[0]

        # Check flashcards with user_id
        cursor.execute("SELECT COUNT(*) FROM flashcards WHERE user_id IS NOT NULL")
        owned_flashcards = cursor.fetchone()[0]

        # Check flashcards without user_id
        cursor.execute("SELECT COUNT(*) FROM flashcards WHERE user_id IS NULL")
        unowned_flashcards = cursor.fetchone()[0]

        print(f"📚 Flashcard ownership status:")
        print(f"   Total flashcards: {total_flashcards}")
        print(f"   Owned flashcards: {owned_flashcards}")
        print(f"   Unowned flashcards: {unowned_flashcards}")

        if unowned_flashcards > 0:
            print("⚠️  Warning: Some flashcards are not owned by any user!")

    except Exception as e:
        print(f"❌ Error checking flashcard ownership: {e}")
    finally:
        conn.close()


def main():
    """Main debugging function."""
    print("🔍 Debugging chinochau database users...")
    print("=" * 60)

    # Check if database exists
    if not check_database_exists():
        return

    # Check if users table exists
    if not check_users_table():
        print(
            "\n💡 Suggestion: Run 'make migrate-db' or 'python migrate_database.py' to create the users table"
        )
        return

    # List all users
    print()
    users = list_all_users()

    # Check flashcard ownership
    print("\n" + "=" * 60)
    check_flashcards_ownership()

    # Provide suggestions
    print("\n" + "=" * 60)
    print("💡 Suggestions:")

    if not users:
        print("   1. Run 'make migrate-db' to create the default admin user")
        print("   2. Or register a new user through the frontend")
        print(
            "   3. Default admin credentials (if created): admin@chinochau.local / admin123"
        )
    else:
        print("   ✅ Users exist in the database")
        print("   - You can log in with any of the users listed above")
        print("   - If you forgot the password, you may need to reset it manually")

    print("\n🚀 Next steps:")
    print("   1. Start backend: make run-backend")
    print("   2. Start frontend: make run-frontend")
    print("   3. Try logging in with existing credentials")


if __name__ == "__main__":
    main()
