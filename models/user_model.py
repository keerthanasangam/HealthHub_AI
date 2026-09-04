from datetime import datetime
from bson.objectid import ObjectId
from database.mongodb import users


class UserModel:

    @staticmethod
    def create_user(name, email, password, role="patient", specialization=None):
        user = {
            "name": name,
            "email": email.lower().strip(),
            "password": password,
            "role": role if role in ["patient", "doctor", "admin"] else "patient",
            "specialization": specialization if role == "doctor" else None,
            "created_at": datetime.utcnow(),
            "profile": {
                "age": None,
                "gender": None,
                "blood_group": None,
                "phone": None
            }
        }

        return users.insert_one(user)

    @staticmethod
    def get_user_by_email(email):
        return users.find_one({
            "email": email.lower().strip()
        })

    @staticmethod
    def get_user_by_id(user_id):
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except Exception:
                return None
        return users.find_one({
            "_id": user_id
        })

    @staticmethod
    def update_profile(user_id, profile_data):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return users.update_one(
            {"_id": user_id},
            {"$set": {"profile": profile_data}}
        )

    @staticmethod
    def get_all_doctors():
        return list(users.find({"role": "doctor"}, {"password": 0}))