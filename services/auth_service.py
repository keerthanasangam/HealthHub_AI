from models.user_model import UserModel
from utils.password import hash_password, verify_password


class AuthService:

    @staticmethod
    def register_user(name, email, password, role="patient", specialization=None):
        if not name or not email or not password:
            return False, "All fields are required"

        if len(password) < 6:
            return False, "Password must be at least 6 characters"

        # Check if email already exists
        existing_user = UserModel.get_user_by_email(email)
        if existing_user:
            return False, "An account with this email already exists"

        # Hash the password
        hashed_password = hash_password(password)

        # Save the user to MongoDB
        result = UserModel.create_user(
            name=name,
            email=email,
            password=hashed_password,
            role=role,
            specialization=specialization
        )

        if result.inserted_id:
            return True, "Registration successful! Please log in."
        return False, "Failed to register user. Please try again."

    @staticmethod
    def authenticate_user(email, password):
        if not email or not password:
            return False, "Email and password are required", None

        user = UserModel.get_user_by_email(email)
        if not user:
            return False, "Invalid email or password", None

        if not verify_password(password, user.get("password")):
            return False, "Invalid email or password", None

        # Build clean session user object (never include password)
        user_session = {
            "id": str(user["_id"]),
            "name": user.get("name", "User"),
            "email": user.get("email"),
            "role": user.get("role", "patient"),
            "specialization": user.get("specialization")
        }

        return True, "Login successful", user_session