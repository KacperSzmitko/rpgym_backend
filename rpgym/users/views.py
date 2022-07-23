from api.mixins import UserPermission
from rest_framework.viewsets import ModelViewSet
from users.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

class UserViewSet(ModelViewSet):
    class UserSerializer(serializers.Serializer):
        pk = serializers.CharField(required=False, default='', read_only=True)
        email = serializers.EmailField(validators=[UniqueValidator(User.objects.all())])
        first_name = serializers.CharField(required=False, default='')
        last_name = serializers.CharField(required=False, default='')
        password = serializers.CharField(required=False, default='', write_only=True)


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


    serializer_class = UserSerializer
    # TODO permission_classes = UserPermission
    queryset = User.objects.all()
