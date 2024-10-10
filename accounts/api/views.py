from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.api.serializers import (
    UserSerializer,
    LoginSerializer,
    SignupSerializer
)
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    serializer_class = SignupSerializer  # 讓瀏覽器介面自動生成輸入表單

    @action(methods=['Get'], detail=False)
    def login_status(self, request):
        print('~~loginstatus', request)
        print(request.user)
        print(type(request.user))
        data = {'has_logged_in': request.user.is_authenticated,
                'ip': request.META['REMOTE_ADDR']}
        print('data', data)
        print(UserSerializer(request.user).data)
        print(type(UserSerializer(request.user)))

        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['Post'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):

        print('request',request)



        # get username and password from request
        serializer = LoginSerializer(data=request.data)

        print('request.user', request.user)
        print('request.data', request.data)

        print('serializer:', serializer, '~~~')

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)

        print('serializer: ', serializer, '~')
        print('serializer.data: ', serializer.data, '~')
        print('serializer.validated_data: ', serializer.validated_data, '~')
        # validation ok, login
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        print("5serializer.validated_data['username']", serializer.validated_data['username'], '~~~')
        user = django_authenticate(username=username, password=password)
        print(user)
        print(type(user))
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "Username and password does not match",
            }, status=400)
        django_login(request, user)
        print('Userserializer(user)', UserSerializer(instance=user))
        print('Userserializer(user).data', UserSerializer(instance=user).data)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['POST'], detail=False)
    def signup(self, request):
        print('request: ', request)
        print('request.data: ', request.data)
        serializer = SignupSerializer(data=request.data)

        print('serializer:', serializer)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)

        user = serializer.save()
        print('user:', user)
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        }, status=201)



