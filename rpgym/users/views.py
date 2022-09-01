from api.mixins import UserPermission
from rest_framework.viewsets import ModelViewSet
from users.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(ModelViewSet):
    class UserSerializer(serializers.Serializer):
        pk = serializers.CharField(required=False, default='', read_only=True)
        email = serializers.EmailField(validators=[UniqueValidator(User.objects.all())])
        first_name = serializers.CharField(required=False, default='')
        last_name = serializers.CharField(required=False, default='')
        password = serializers.CharField(required=False, default='', write_only=True)
        wieght = serializers.FloatField()
        max_cycle = serializers.FloatField()
        current_cycle = serializers.FloatField()


        def create(self, validated_data):
            user = User(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
            return user

        def update(self, instance, validated_data):
            if 'password' in validated_data:
                instance.set_password(validated_data['password'])
            instance.save()
            return instance


    @action(detail=False, methods=['get'])
    def own(self, request):
        """Get current logged user object or 401
        """
        if request.user.is_authenticated:
            queryset = request.user
            serializer = self.get_serializer_class()(queryset)
            return Response(serializer.data)
        return Response(status=401)

    serializer_class = UserSerializer
    # TODO permission_classes = UserPermission
    queryset = User.objects.all()
