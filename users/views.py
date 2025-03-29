from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .serializers import UserSerializer

User = get_user_model()

@api_view(['GET'])
def users(request):
    users = User.objects.all()
    data = UserSerializer(users, many=True, context={'request': request}).data
    return Response(data)

@api_view(['GET'])
def user(request, pk):
    user = User.objects.get(id = pk)
    data = UserSerializer(user , many=False, context={'request': request}).data
    return Response(data)

@api_view(['POST'])
def register(request):
    data = request.data
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    # role = data.get('role')

    if not username or not email or not password:
        return Response({"error": "Tous les champs sont obligatoires"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Ce nom d'utilisateur existe déjà"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({"message": "Utilisateur créé avec succès"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = User.objects.filter(username=username).first()
    if user is None or not user.check_password(password):
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        "id": user.id,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "role": user.role 
    })
