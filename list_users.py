#!/usr/bin/env python3
"""
Script: list_users.py
Shows all registered users from the DermaFlow database.
Note: Passwords are intentionally NOT included (hashed, can't be decoded).
Usage: python list_users.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from backend.database import SessionLocal
from backend.models import User


def list_users():
    try:
        db = SessionLocal()
        users = db.query(User).all()

        if not users:
            print("No users found in the database.")
            return

        print("=" * 80)
        print(f"{'Registered Users':^80}")
        print("=" * 80)
        print(f"{'ID':<5} {'Email':<30} {'Role':<15} {'Name':<25} {'Active':<7}")
        print("-" * 80)

        for user in users:
            name = f"{user.first_name} {user.last_name}"
            print(f"{user.id:<5} {user.email:<30} {user.role:<15} {name:<25} {'Yes' if user.is_active else 'No':<7}")

        print("-" * 80)
        print(f"Total users: {len(users)}")

        # Show counts by role
        from collections import Counter
        role_counts = Counter(u.role for u in users)
        print("\nUsers by role:")
        for role, count in role_counts.items():
            print(f"  - {role}: {count}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    list_users()
