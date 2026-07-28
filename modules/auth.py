"""
Authentication management for FEST application.
Handles user registration, login, and session management.
"""

import os
import hashlib
import pandas as pd
from modules.theme import ThemeManager


class AuthManager:
    """Manages user authentication and sessions."""

    def __init__(self):
        self.current_user = None
        self.theme = ThemeManager()
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.users_file = os.path.join(self.base_dir, "users.csv")

    def hash_password(self, password):
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def load_users(self):
        """Load users from CSV file."""
        if not os.path.exists(self.users_file):
            return {}
        try:
            df = pd.read_csv(self.users_file, dtype=str, keep_default_na=False)
            return dict(zip(df["id"], df["password"]))
        except (pd.errors.EmptyDataError, KeyError):
            return {}

    def save_user(self, user_id, hashed_password):
        """Save a new user to the CSV file."""
        exists = os.path.exists(self.users_file)
        row = pd.DataFrame([{"id": user_id, "password": hashed_password}])
        row.to_csv(self.users_file, mode="a", header=not exists, index=False)

    def register(self, user_id, password, confirm_password):
        """Register a new user."""
        user_id = user_id.strip()

        if not user_id or not password:
            return False, "User ID and password are required."

        if len(password) < 4:
            return False, "Password must be at least 4 characters."

        if password != confirm_password:
            return False, "Passwords do not match."

        if user_id in self.load_users():
            return False, f"User ID '{user_id}' is already taken."

        self.save_user(user_id, self.hash_password(password))
        return True, f"Account '{user_id}' created successfully!"

    def login(self, user_id, password):
        """Log in a user."""
        user_id = user_id.strip()

        if not user_id or not password:
            return False, "Enter your ID and password."

        users = self.load_users()
        if user_id not in users or users[user_id] != self.hash_password(password):
            return False, "Invalid ID or password."

        self.current_user = user_id
        return True, f"Welcome back, {user_id}!"

    def logout(self):
        """Log out the current user."""
        self.current_user = None
        return True, "Logged out successfully."

    def is_authenticated(self):
        """Check if a user is currently logged in."""
        return self.current_user is not None