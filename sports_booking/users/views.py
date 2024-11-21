from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer, UserSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
)
from rest_framework.views import APIView

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                #basic
                return Response({"message": "If the email exists, a reset link has been sent."})
                # token = default_token_generator.make_token(user)
                # uid = urlsafe_base64_encode(force_bytes(user.pk))
                # reset_link = f"http://localhost:8000/reset-password/?uid={uid}&token={token}"
                # send_mail(
                #     "Password Reset Request",
                #     f"Click the link to reset your password: {reset_link}",
                #     "noreply@example.com",
                #     [email],
                #     fail_silently=False,
                # )
            return Response({"message": "If the email exists, a reset link has been sent."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            uid = request.GET.get('uid')
            token = request.data['token']
            password = serializer.validated_data['password']
            try:
                user_id = force_str(urlsafe_base64_decode(uid))
                user = User.objects.get(pk=user_id)
                if default_token_generator.check_token(user, token):
                    user.set_password(password)
                    user.save()
                    return Response({"message": "Password reset successful"})
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                pass
        return Response({"error": "Invalid reset link"}, status=status.HTTP_400_BAD_REQUEST)
