from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
@api_view(['POST'])
@permission_classes([AllowAny])
@transaction.atomic
def Register(request):

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
            username=username,
            email=email,
            password=password,
            role=role,
            phone_number=phone_number
        )

        return Response({'message': 'User created successfully'}, status=201)

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
      'refresh':str(refresh),
      'access':str(refresh.access_token),
      'user':{
        'id':user.id,
        'username':user.username,
        'email':user.email,
        'role':user.role,
        'phone_number':user.phone_number
      }
    },status=200)
  else:
    return Response({'error':'Invalid credentials'},status=401)
