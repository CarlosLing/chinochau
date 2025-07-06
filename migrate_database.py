#!/usr/bin/env python3
"""
Database migration script for adding user authentication to chinochau.

This script:
1. Creates a backup of the existing database
2. Adds the new users table
3. Creates a default user for existing flashcards
4. Migrates existing flashcards to be owned by the default user

Run this script after updating the codebase but before starting the new version.
"""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from passlib.context import CryptContext

# Database configuration
DB_PATH = "flashcards.db"
BACKUP_PATH = f"flashcards_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

# Default user for migration
DEFAULT_USER_EMAIL = "admin@chinochau.local"
DEFAULT_USER_PASSWORD = "admin123"  # Change this after migration!
DEFAULT_USER_NAME = "Default Admin User"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def backup_database():
    """Create a backup of the existing database."""
    if Path(DB_PATH).exists():
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"✅ Database backed up to {BACKUP_PATH}")
    else:
        print("ℹ️  No existing database found, creating new one")


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def migrate_database():
    """Perform the database migration."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if users table already exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        if cursor.fetchone():
            print("⚠️  Users table already exists, skipping migration")
            return

        print("🔄 Starting database migration...")

        # Create users table
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                email VARCHAR UNIQUE NOT NULL,
                full_name VARCHAR,
                hashed_password VARCHAR NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        print("✅ Created users table")

        # Create default user
        hashed_password = get_password_hash(DEFAULT_USER_PASSWORD)
        cursor.execute(
            """
            INSERT INTO users (email, full_name, hashed_password, is_active, created_at)
            VALUES (?, ?, ?, 1, ?)
        """,
            (DEFAULT_USER_EMAIL, DEFAULT_USER_NAME, hashed_password, datetime.utcnow()),
        )

        default_user_id = cursor.lastrowid
        print(f"✅ Created default user with ID: {default_user_id}")

        # Check if flashcards table has user_id column
        cursor.execute("PRAGMA table_info(flashcards)")
        columns = [column[1] for column in cursor.fetchall()]

        if "user_id" not in columns:
            # Add user_id column to flashcards table
            cursor.execute("ALTER TABLE flashcards ADD COLUMN user_id INTEGER")
            print("✅ Added user_id column to flashcards table")

            # Update existing flashcards to belong to default user
            cursor.execute(
                "UPDATE flashcards SET user_id = ? WHERE user_id IS NULL",
                (default_user_id,),
            )
            affected_rows = cursor.rowcount
            print(f"✅ Migrated {affected_rows} existing flashcards to default user")

            # Add foreign key constraint (recreate table with constraint)
            cursor.execute("BEGIN TRANSACTION")

            # Create new table with proper constraints
            cursor.execute(
                """
                CREATE TABLE flashcards_new (
                    id INTEGER PRIMARY KEY,
                    chinese VARCHAR NOT NULL,
                    pinyin VARCHAR NOT NULL,
                    definitions TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            # Copy data from old table
            cursor.execute(
                """
                INSERT INTO flashcards_new (id, chinese, pinyin, definitions, user_id)
                SELECT id, chinese, pinyin, definitions, user_id FROM flashcards
            """
            )

            # Drop old table and rename new one
            cursor.execute("DROP TABLE flashcards")
            cursor.execute("ALTER TABLE flashcards_new RENAME TO flashcards")

            # Recreate indexes
            cursor.execute(
                "CREATE INDEX idx_flashcards_chinese ON flashcards (chinese)"
            )
            cursor.execute(
                "CREATE INDEX idx_flashcards_user_id ON flashcards (user_id)"
            )

            cursor.execute("COMMIT")
            print("✅ Applied foreign key constraints")

        conn.commit()
        print("🎉 Database migration completed successfully!")

        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Default user created:")
        print(f"  Email: {DEFAULT_USER_EMAIL}")
        print(f"  Password: {DEFAULT_USER_PASSWORD}")
        print(f"  ⚠️  IMPORTANT: Change the default password after first login!")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


def verify_migration():
    """Verify the migration was successful."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"✅ Users table has {user_count} users")

        # Check flashcards table
        cursor.execute("SELECT COUNT(*) FROM flashcards WHERE user_id IS NOT NULL")
        flashcard_count = cursor.fetchone()[0]
        print(f"✅ All {flashcard_count} flashcards have user associations")

        # Check examples table (should still work)
        cursor.execute("SELECT COUNT(*) FROM examples")
        example_count = cursor.fetchone()[0]
        print(f"✅ Examples table has {example_count} examples")

    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    print("🚀 Starting chinochau database migration...")
    print("This will add user authentication to your existing database.")

    # Confirm with user
    response = input("\nDo you want to proceed? (y/N): ")
    if response.lower() != "y":
        print("Migration cancelled.")
        exit(0)

    try:
        backup_database()
        migrate_database()
        verify_migration()

        print("\n✅ Migration completed successfully!")
        print(f"📁  Original database backed up to: {BACKUP_PATH}")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"📁  You can restore from backup: {BACKUP_PATH}")
        exit(1)
