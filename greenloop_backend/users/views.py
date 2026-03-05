from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer,UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import User
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from pickup.models import Pickup
from pickup.serializers import PickupSerializer
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
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



class PickupViewSet(viewsets.ModelViewSet):

    serializer_class = PickupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role == "admin":
            return Pickup.objects.all()

        return Pickup.objects.filter(resident=user)

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)
        
        

@api_view(['POST'])
def forgot_password(request):

    email = request.data.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error":"User not found"}, status=404)

    token = default_token_generator.make_token(user)

    reset_link = f"http://127.0.0.1:8000/reset-password/{user.id}/{token}/"

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
    user.set_password(new_password)
    user.save()

    return Response({"message":"Password reset successful"})