from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from .models import UserProfile


# =========================================================
# SIGN UP
# =========================================================

def signup(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        role = request.POST.get(
            "role",
            ""
        )

        # Check passwords
        if password != confirm_password:

            return render(
                request,
                "users/signup.html",
                {
                    "error": "Passwords do not match."
                }
            )

        # Check username
        if User.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                "users/signup.html",
                {
                    "error": "Username already exists."
                }
            )

        # Check role
        if role not in [
            "examiner",
            "test_taker"
        ]:

            return render(
                request,
                "users/signup.html",
                {
                    "error": "Please select a valid role."
                }
            )

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create profile
        UserProfile.objects.create(
            user=user,
            role=role
        )

        # Log the user in
        login(request, user)

        # Redirect based on role
        if role == "examiner":

            return redirect(
                "examiner_dashboard"
            )

        return redirect(
            "test_list"
        )

    return render(
        request,
        "users/signup.html"
    )


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            profile = UserProfile.objects.get(
                user=user
            )

            # Examiner
            if profile.role == "examiner":

                return redirect(
                    "examiner_dashboard"
                )

            # Test Taker
            return redirect(
                "test_list"
            )

        return render(
            request,
            "users/login.html",
            {
                "error": "Invalid username or password."
            }
        )

    return render(
        request,
        "users/login.html"
    )