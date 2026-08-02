from tokenize import TokenError

from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

from rest_framework import request, request, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

from core.serializers import StaffSerializer

from .models import *
@api_view(['POST'])
@permission_classes([IsAdminUser])
@transaction.atomic
def Register(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    role = request.data.get('role')
    phone_number = request.data.get('phone_number')

    VALID_ROLES = ["admin", "staff"]

    if not all([username, email, password, role, phone_number]):
        return Response({'error': 'All fields are required'}, status=400)

    if role not in VALID_ROLES:
        return Response({'error': 'Invalid role'}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({'error': 'Email already exists'}, status=400)

    try:
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
            role=role,
            phone_number=phone_number
        )
        if role == "staff":
            user.is_staff = True
            user.save()

        return Response({
                "user_id":user.id,
                "username":user.username,
                "role":user.role,
                "message":f"{role.capitalize()} Registered successfuly"
        })

    except IntegrityError:
        return Response({'error': 'Database error'}, status=400)
    except Exception as e:
        return Response({"error":str(e)})

# login
@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
  username=request.data.get('username')
  password=request.data.get('password')

  if not username or not password:
    return Response({'error':'Username and password are required'},status=400)

  user=authenticate(username=username,password=password)
  if user is not None:
    refresh=RefreshToken.for_user(user)
    return Response({
    'user':{
        'id':user.id,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'username':user.username,
        'email':user.email,
        'role':user.role,
        'phone_number':user.phone_number
    },
    'refresh':str(refresh),
      'access':str(refresh.access_token),
    },status=200)
  else:
    return Response({'error':'Invalid credentials'},status=401)

# logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Logout(request):
    try:
        refresh_token=request.data.get("refresh")
        token=RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message":"Logout successful"},status=200)
    except TokenError:
        return Response({"message": "Invalid or expired token"})
    except Exception as e:
        return Response({"error":str(e)})


from .serializers import ProfileSerializer

@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def Profile(request):

    if request.method == "GET":
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    serializer = ProfileSerializer(
        request.user,
        data=request.data,
        partial=True
    )

    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Profile updated successfully.",
            "user": serializer.data
        })

    return Response(serializer.errors, status=400)

# admin to view staff and cars sold
class StaffViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(role='staff')
    serializer_class = StaffSerializer
    permission_classes = [IsAdminUser]
    def get_queryset(self):
        queryset = super().get_queryset()
        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.filter(username__icontains=username)
        return queryset

from .serializers import ChangePasswordSerializer

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ChangePassword(request):

    serializer = ChangePasswordSerializer(data=request.data)

    if serializer.is_valid():

        user = request.user

        if not user.check_password(
            serializer.validated_data["current_password"]
        ):
            return Response(
                {"error": "Current password is incorrect."},
                status=400
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response({
            "message": "Password changed successfully."
        })

    return Response(serializer.errors, status=400)


@api_view(["PATCH"])
@permission_classes([IsAdminUser])
def togglestaff_status(request, id):

    try:
        staff = User.objects.get(
            id=id,
            role="staff"
        )

    except User.DoesNotExist:
        return Response(
            {"error": "Staff member not found"},
            status=404
        )

    staff.is_active = not staff.is_active
    staff.save()

    return Response({
        "message": "Staff status updated",
        "is_active": staff.is_active
    })
