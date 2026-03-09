from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from .models import User

from pickup.models import Pickup
from pickup.serializers import PickupSerializer

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

def get_tokens(user):

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():

        user = serializer.save()
        tokens = get_tokens(user)

        return Response({
            "message":"User created",
            "tokens":tokens
        })

    return Response(serializer.errors)


@api_view(['POST'])
def login(request):

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():

        user = serializer.validated_data
        tokens = get_tokens(user)

        return Response({
            "username":user.username,
            "role":user.role,
            "tokens":tokens
        })

    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_users(request):

    # allow only admin
    if request.user.role != "admin":
        return Response({"error":"Access denied"}, status=403)

    users = User.objects.all()

    serializer = UserSerializer(users, many=True)

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):

    # only admin allowed
    if request.user.role != "admin":
        return Response({"error": "Access denied"}, status=403)

    total_users = User.objects.count()
    total_residents = User.objects.filter(role="resident").count()
    total_admins = User.objects.filter(role="admin").count()

    total_pickups = Pickup.objects.count()
    pending_pickups = Pickup.objects.filter(status="pending").count()
    collected_pickups = Pickup.objects.filter(status="collected").count()

    return Response({
        "total_users": total_users,
        "total_residents": total_residents,
        "total_admins": total_admins,
        "total_pickups": total_pickups,
        "pending_pickups": pending_pickups,
        "collected_pickups": collected_pickups
    })
        
        

@api_view(['POST'])
def forgot_password(request):

    email = request.data.get("email")

    try:
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message":"If email exists, reset link sent"})
    except User.DoesNotExist:
        return Response({"error":"User not found"}, status=404)

    token = default_token_generator.make_token(user)

    reset_link = f"http://127.0.0.1:8000/api/auth/reset-password/{user.id}/{token}/"

    send_mail(
        "Password Reset",
        f"Click the link to reset your password: {reset_link}",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    return Response({"message":"Password reset link sent to email"})


@api_view(['POST'])
def reset_password(request, uid, token):

    try:
        user = User.objects.get(id=uid)
    except User.DoesNotExist:
        return Response({"error":"Invalid user"}, status=404)

    if not default_token_generator.check_token(user, token):
        return Response({"error":"Invalid or expired token"}, status=400)

    new_password = request.data.get("password")
    if not new_password:
        return Response({"error": "Password is required"}, status=400)
    user.set_password(new_password)
    user.save()

    return Response({"message":"Password reset successful"})



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):

    user = request.user

    serializer = UserSerializer(user)

    return Response(serializer.data)


@api_view(['GET','PATCH'])
@permission_classes([IsAuthenticated])
def my_profile(request):

    user = request.user

    # GET → view profile
    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # PATCH → update profile
    if request.method == "PATCH":
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)