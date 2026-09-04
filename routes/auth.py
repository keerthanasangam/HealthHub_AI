from flask import Blueprint
from controllers.auth_controller import AuthController

auth = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth.route("/register", methods=["GET", "POST"])
def register():
    return AuthController.register()


@auth.route("/login", methods=["GET", "POST"])
def login():
    return AuthController.login()


@auth.route("/logout", methods=["GET"])
def logout():
    return AuthController.logout()