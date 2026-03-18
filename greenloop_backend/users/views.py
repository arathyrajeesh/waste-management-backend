from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, HKSWorkerCreationSerializer, HKSWorkerLocationSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
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


@extend_schema(
    request=HKSWorkerCreationSerializer,
    responses={201: OpenApiResponse(description='HKS Worker created successfully')},
    summary='Create HKS Worker',
    description='Admin only: Create a new HKS (Household Keeping Staff) worker account.',
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_hks_worker(request):
    
    # allow only admin
    if request.user.role != "admin":
        return Response({"error":"Access denied"}, status=403)

    serializer = HKSWorkerCreationSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response({
            "message": "HKS Worker created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=RegisterSerializer,
    responses={201: OpenApiResponse(description='User created successfully with tokens')},
    summary='Register',
    description='Register a new resident or recycler account.',
)
@api_view(['POST'])
def register(request):

    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        tokens = get_tokens(user)

        return Response({
            "message": "User created successfully",
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    request=LoginSerializer,
    responses={200: OpenApiResponse(description='Returns user info and JWT tokens')},
    summary='Login',
    description='Login with email and password to get JWT access and refresh tokens.',
)
@api_view(['POST'])
def login(request):

    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():

        user = serializer.validated_data
        tokens = get_tokens(user)

        return Response({
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "tokens": tokens
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    responses={200: UserSerializer(many=True)},
    summary='All Users',
    description='Admin only: List all users. Optionally filter by role using ?role=<role>. DELETE to remove a user by providing user_id in the request body.',
)
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def all_users(request):

    # allow only admin
    if request.user.role != "admin":
        return Response({"error":"Access denied"}, status=403)

    if request.method == 'GET':
        # Optional filtering by role
        role_filter = request.GET.get('role')
        if role_filter:
            users = User.objects.filter(role=role_filter)
        else:
            users = User.objects.all()

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
        
    elif request.method == 'DELETE':
        user_id = request.data.get('user_id')
        if not user_id:
             return Response({"error": "user_id is required"}, status=400)
             
        try:
            user_to_delete = User.objects.get(id=user_id)
            if user_to_delete.role == 'admin':
                return Response({"error": "Cannot delete admin users"}, status=403)
            user_to_delete.delete()
            return Response({"message": "User deleted successfully"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


@extend_schema(
    responses={200: OpenApiResponse(description='Admin dashboard summary stats (total users, pickups, etc.)')},
    summary='Admin Dashboard',
    description='Admin only: Get high-level summary stats for the admin dashboard.',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):

    # only admin allowed
    if request.user.role != "admin":
        return Response({"error": "Access denied"}, status=403)

    total_users = User.objects.count()
    total_residents = User.objects.filter(role="resident").count()
    total_workers = User.objects.filter(role="hks_worker").count()
    total_admins = User.objects.filter(role="admin").count()

    total_pickups = Pickup.objects.count()
    pending_pickups = Pickup.objects.filter(status="pending").count()
    collected_pickups = Pickup.objects.filter(status="collected").count()

    return Response({
        "total_users": total_users,
        "total_residents": total_residents,
        "total_workers": total_workers,
        "total_admins": total_admins,
        "total_pickups": total_pickups,
        "pending_pickups": pending_pickups,
        "collected_pickups": collected_pickups
    })
        
        
@extend_schema(
    responses={200: OpenApiResponse(description='Returns worker locations and pending pickups for the live map.')},
    summary='Admin Live Map',
    description='Admin only: Get current HKS worker locations and pending pickups for the live map view.',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_live_map(request):
    if request.user.role != "admin":
        return Response({"error": "Access denied"}, status=403)

    # Get active workers (could filter by online status if we had one)
    workers = User.objects.filter(role='hks_worker')
    worker_data = HKSWorkerLocationSerializer(workers, many=True).data

    # Get pending pickups (for display on the map)
    pending_pickups = Pickup.objects.filter(status='pending')
    pickup_data = PickupSerializer(pending_pickups, many=True).data

    return Response({
        "workers": worker_data,
        "pending_pickups": pickup_data
    })


@extend_schema(
    responses={200: OpenApiResponse(description='Returns pickup and complaint stats grouped by ward.')},
    summary='Admin Ward Monitoring',
    description='Admin only: Get pickup completion and complaint stats for each ward.',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_ward_monitoring(request):
    if request.user.role != "admin":
        return Response({"error": "Access denied"}, status=403)

    from django.db.models import Count, Q
    
    # Group users by ward
    wards = User.objects.exclude(ward='').values_list('ward', flat=True).distinct()
    
    ward_data = []
    for ward in wards:
        # Residents in this ward
        residents = User.objects.filter(role='resident', ward=ward)
        
        # Pickups in this ward
        pickups = Pickup.objects.filter(resident__in=residents)
        total_pickups = pickups.count()
        completed_pickups = pickups.filter(status='collected').count()
        
        # Complaints in this ward
        from complaints.models import Complaint
        complaints = Complaint.objects.filter(resident__in=residents).count()
        
        ward_data.append({
            "ward": ward,
            "total_pickups": total_pickups,
            "completed_pickups": completed_pickups,
            "complaints": complaints
        })

    return Response(ward_data)

@extend_schema(
    responses={200: OpenApiResponse(description='Returns all complaints with stats.')},
    summary='Admin Complaints',
    description='Admin only: Get all complaints with total, pending, and resolved counts.',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_complaints(request):
    if request.user.role != "admin":
        return Response({"error": "Access denied"}, status=403)

    from complaints.models import Complaint
    from complaints.serializers import ComplaintSerializer

    # Get all complaints
    complaints = Complaint.objects.all().order_by('-created_at')
    
    # We can use the existing serializer which now includes assigned worker info
    serializer = ComplaintSerializer(complaints, many=True)
    
    # Send some stats as well
    total = complaints.count()
    pending = complaints.filter(status='pending').count()
    resolved = complaints.filter(status='resolved').count()

    return Response({
        "stats": {
            "total": total,
            "pending": pending,
            "resolved": resolved
        },
        "complaints": serializer.data
    })


@extend_schema(
    responses={200: OpenApiResponse(description='Returns fee collection stats and per-pickup details.')},
    summary='Admin Fee Collection',
    description='Admin only: Get fee collection stats (total expected, collected, pending).',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_fees(request):
    if request.user.role != "admin":
        return Response({"error": "Access denied"}, status=403)

    from django.db.models import Sum
    
    # Get all pickups that have a fee > 0
    pickups = Pickup.objects.filter(fee_amount__gt=0).order_by('-date')

    # Calculate stats
    total_fee_expected = pickups.aggregate(Sum('fee_amount'))['fee_amount__sum'] or 0
    total_fee_collected = pickups.filter(fee_paid=True).aggregate(Sum('fee_amount'))['fee_amount__sum'] or 0
    pending_fee = total_fee_expected - total_fee_collected

    # Get details
    fee_details = []
    for pickup in pickups:
        fee_details.append({
            "id": pickup.id,
            "resident": pickup.resident.username,
            "ward": pickup.resident.ward,
            "fee_amount": pickup.fee_amount,
            "fee_paid": pickup.fee_paid,
            "date": pickup.date
        })

    return Response({
        "stats": {
            "total_expected": total_fee_expected,
            "total_collected": total_fee_collected,
            "pending": pending_fee
        },
        "details": fee_details
    })

@extend_schema(
    responses={200: OpenApiResponse(description='Returns waste stats broken down by type (dry, wet, e-waste, biomedical).')},
    summary='Admin Waste Reports',
    description='Admin only: Get collected waste stats broken down by waste type.',
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard_waste_reports(request):
    if request.user.role != "admin":
        return Response({"error": "Access denied"}, status=403)

    from django.db.models import Sum
    
    # Get all collected pickups
    pickups = Pickup.objects.filter(status='collected')

    # Calculate stats by waste type
    dry_waste = pickups.filter(waste_type='dry').aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
    wet_waste = pickups.filter(waste_type='wet').aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
    e_waste = pickups.filter(waste_type='e-waste').aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0
    biomedical_waste = pickups.filter(waste_type='biomedical').aggregate(Sum('weight_kg'))['weight_kg__sum'] or 0

    return Response({
        "total_weight_kg": dry_waste + wet_waste + e_waste + biomedical_waste,
        "breakdown": {
            "dry": dry_waste,
            "wet": wet_waste,
            "e-waste": e_waste,
            "biomedical": biomedical_waste
        }
    })

@extend_schema(
    request=ForgotPasswordSerializer,
    responses={200: OpenApiResponse(description='Password reset link sent to email')},
    summary='Forgot Password',
    description='Send a password reset link to the provided email address.',
)
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


@extend_schema(
    request=ResetPasswordSerializer,
    responses={200: OpenApiResponse(description='Password reset successful')},
    summary='Reset Password',
    description='Reset the password using the uid and token from the reset email link.',
)
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


@extend_schema(
    request=UserSerializer,
    responses={200: UserSerializer},
    summary='My Profile',
    description='GET your own profile. PATCH to update fields like phone, ward, etc.',
)
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
