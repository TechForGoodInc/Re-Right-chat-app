from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListAPIView
from .serializers import RegistrationSerializer, UserSerializer, UsersSerializer
# from serializers.user_serializer import UsersSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import serializers, viewsets
from .models import User
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from filters.filter import UserSearchFilter


# checks and create user.
@api_view(['POST', ])
def registration_view(request):
    if request.method == 'POST':
        data = {}
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            data['response'] = 'successfully registered new user.'
            # data['email'] = account.email
            # data['username'] = account.username
            # token = Token.objects.get(user=account).key
            # data['token'] = token
        else:
            data = serializer.errors
        return Response(data)


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'put', 'delete']
    permission_classes = [IsAuthenticated]
    @action(detail=True, methods=['PUT'])
    # this method is for updating user related details.
    def update_user(self, request, pk=None):
        user = User.objects.get(id=pk)
        if 'username' in request.data:
            setattr(user, "username", request.data['username'])
            user.save()
        serializer = UserSerializer(user, many=False)
        return Response(serializer.data)


class userView(RetrieveUpdateDestroyAPIView):
    ''' View for managing specific user '''
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class searchUserView(ListAPIView):
    '''gets a list of user, or create a new user'''
    permission_classes = (AllowAny,)
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserSearchFilter

    print(queryset)
# to design a custom authentication.


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # in cutome User model email is essential for login but internally User takes
        # username attribute in django.
        if User.objects.filter(email=request.data['username']).exists():
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            print(request.data)
            if serializer.is_valid():
                print(request.data)
                user = serializer.validated_data['user']
                token, created = Token.objects.get_or_create(user=user)
                user_data = UserSerializer(user).data
                return Response({
                    'token': token.key,
                })

            return Response({"chk_uname_or_pwd": "Please check your Password"},
                            status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"user_not_found": "User does not exists with this email address"},
                            status=status.HTTP_404_NOT_FOUND)
