from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from firebase_admin import auth
import firebase_admin
from user.models import User_Data
import logging

logger = logging.getLogger(__name__)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        firebase_token = request.data.get("firebase_token")
        user = None
        logger.info(f"{firebase_token}")
        if firebase_token:
            try:
                decoded_token = auth.verify_id_token(firebase_token)
                email = decoded_token.get("email")

                if not email:
                    return Response(
                        {"detail": "Firebase token must contain an email."}, status=400
                    )
                user, created = User.objects.get_or_create(
                    username=email, defaults={"email": email}
                )
                if created:
                    user.set_unusable_password()
                    user.save()
            except Exception as e:
                # logger.error(f"Firebase token verification failed: {e}", exc_info=True)
                return Response(
                    {"detail": "Invalid Firebase token", "error": str(e)},
                    status=400,
                )
        else:
            username = request.data.get("username")
            password = request.data.get("password")
            user = authenticate(request, username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response = Response({"detail": "Login successful"})
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=1800,
            )
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,
                samesite="Lax",
                max_age=86400,
            )
            return response
        return Response({"detail": "Invalid credentials"}, status=400)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token missing"}, status=400)

        try:
            refresh = RefreshToken(refresh_token)
            new_access = str(refresh.access_token)
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=400)

        response = Response({"detail": "Token refreshed"})
        response.set_cookie(
            key="access_token",
            value=new_access,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=1800,
        )
        return response


class LogoutView(APIView):
    def post(self, request):
        response = Response({"detail": "Logout successful"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        )
