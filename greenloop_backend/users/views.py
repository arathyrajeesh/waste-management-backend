from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer


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


from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer


@api_view(['GET'])
def all_users(request):

    # allow only admin
    if request.user.role != "admin":
        return Response({"error":"Access denied"}, status=403)

    users = User.objects.all()

    serializer = UserSerializer(users, many=True)

    return Response(serializer.data)