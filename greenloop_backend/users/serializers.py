from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username','email','password','phone','ward','role')

    def validate_role(self, value):
        # Allow admins to set any role
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated and request.user.role == 'admin':
            return value

        # allow only resident and recycler registration
        allowed_roles = ['resident', 'recycler']

        if value not in allowed_roles:
            raise serializers.ValidationError("You cannot register with this role")

        return value

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            ward=validated_data['ward'],
            role=validated_data.get('role','resident'),
        )

        return user

class HKSWorkerCreationSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username','email','password','phone','ward')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data['phone'],
            ward=validated_data.get('ward', ''),
            role='hks_worker'
        )
        return user
    

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):

        email = data.get("email")
        password = data.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        return user
    

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id','username','email','phone','ward','role', 'location', 'last_location_update']
        read_only_fields = ['id', 'role']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'ward', 'location']


class HKSWorkerLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'phone', 'ward', 'latitude', 'longitude', 'last_location_update']

    def get_latitude(self, obj):
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        return obj.location.x if obj.location else None

class UpdateLocationSerializer(serializers.Serializer):
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)