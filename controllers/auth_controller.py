from flask import render_template, request, redirect, url_for, flash, session
from services.auth_service import AuthService


class AuthController:

    @staticmethod
    def register():
        if session.get("user"):
            return redirect(url_for("patient.dashboard" if session["user"].get("role") != "doctor" else "doctor.dashboard"))

        if request.method == "GET":
            return render_template("auth/register.html")

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "patient")
        specialization = request.form.get("specialization", "").strip() if role == "doctor" else None

        success, message = AuthService.register_user(
            name=name,
            email=email,
            password=password,
            role=role,
            specialization=specialization
        )

        if success:
            flash(message, "success")
            return redirect(url_for("auth.login"))

        flash(message, "danger")
        return redirect(url_for("auth.register"))

    @staticmethod
    def login():
        if session.get("user"):
            return redirect(url_for("patient.dashboard" if session["user"].get("role") != "doctor" else "doctor.dashboard"))

        if request.method == "GET":
            return render_template("auth/login.html")

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        success, message, user_data = AuthService.authenticate_user(email, password)

        if success and user_data:
            session["user"] = user_data
            flash(f"Welcome back, {user_data['name']}!", "success")
            if user_data.get("role") == "doctor":
                return redirect(url_for("doctor.dashboard"))
            return redirect(url_for("patient.dashboard"))

        flash(message, "danger")
        return redirect(url_for("auth.login"))

    @staticmethod
    def logout():
        session.pop("user", None)
        flash("You have been signed out safely.", "success")
        return redirect(url_for("auth.login"))