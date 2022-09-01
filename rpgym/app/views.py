from statistics import StatisticsError, mean
from django.forms import IntegerField
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import generics, serializers, pagination, mixins
from app.models import MusclePart, TrainHistory, TrainPlan, PlanModule, TrainModule, Exercise
from common.utils import inline_serializer
from rest_framework.request import Request
from rest_framework.response import Response
from django.db.models import Q
from attrs import define
from rest_framework.permissions import IsAuthenticated
from users.models import User
from django.db import IntegrityError
from rest_framework.decorators import action
from django.db.models.query import QuerySet

class MusclePartsView(ModelViewSet):
    class MusclePartSeriazlier(serializers.ModelSerializer):
        class Meta:
            model = MusclePart
            fields = '__all__'
    queryset = MusclePart.objects.all()
    serializer_class = MusclePartSeriazlier


class MuscleLevelList(APIView):

    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.Serializer):
        muscle_name = serializers.CharField()
        level = serializers.IntegerField()
        progress = serializers.FloatField()

    @define
    class OutputModel:
        muscle_name: str
        level: int
        progress: float

    def get(self, request: Request):
        result = []
        muscles = MusclePart.objects.all()
        user_modules = PlanModule.objects.filter(module__user=request.user)

        for muscle in muscles:
            user_muscle_modules = user_modules.filter(
                module__exercise__muscle_part=muscle)
            units_progres, levels = [], []
            for user_muscle_module in user_muscle_modules:
                # For every muscle part get levels from every train module using this part
                levels.append(user_muscle_module.module.current_level)
                units_progres.append(user_muscle_module.module.progress)
            try:
                result.append(self.OutputModel(
                    muscle.name, int(mean(levels)), mean(units_progres)))
            except StatisticsError:
                result.append(self.OutputModel(
                    muscle.name, 0, 0))
        result = self.OutputSerializer(result, many=True)
        return Response(result.data)


class TrainModuleViewSet(ModelViewSet):
    class Pagination(pagination.PageNumberPagination):
        page_size = 5
        max_page_size = 40
        page_query_param = "page"
        page_size_query_param = "page_size"

    class OutputSerializer(serializers.ModelSerializer):
        exercise = serializers.SerializerMethodField()
        muscle_part_id = serializers.SerializerMethodField()

        class Meta:
            model = TrainModule
            exclude = ('user', 'creation_date')

        def get_exercise(self, obj):
            return obj.exercise.id

        def get_muscle_part_id(self, obj):
            return obj.exercise.muscle_part.id

    class InputSerializer(serializers.ModelSerializer):
        user = serializers.SlugRelatedField(slug_field='id', read_only=True)
        exercise = serializers.PrimaryKeyRelatedField(
            read_only=False, queryset=Exercise.objects.all())
        id = IntegerField(required=False)

        class Meta:
            model = TrainModule
            fields = ('name',
                      'exercise',
                      'series',
                      'weight',
                      'level_weight_increase',
                      'reps',
                      'user',
                      'id')

        def validate(self, attrs):
            if attrs['series'] != len(attrs['reps']):
                raise serializers.ValidationError(
                    {"detail": "Serie number doesnt match reps number"})
            return super().validate(attrs)

    def create(self, request, *args, **kwargs):
        serialzier = self.get_serializer(data=request.data)
        serialzier.is_valid(raise_exception=True)
        obj = serialzier.save(user=self.request.user)
        result = self.OutputSerializer(obj)
        return Response(data=result.data, status=201)

    @action(detail=False, methods=['get'])
    def all(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    serializer_class = OutputSerializer

    def get_queryset(self) -> QuerySet:
        return TrainModule.objects.filter(user=self.request.user)

    def get_serializer_class(self) -> serializers.Serializer:
        if self.request.method == 'GET':
            return self.OutputSerializer
        return self.InputSerializer


class PlanViewSet(ModelViewSet):
    class Pagination(pagination.PageNumberPagination):
        page_size = 5
        max_page_size = 40
        page_query_param = "page"
        page_size_query_param = "page_size"

    class OutputSerializer(serializers.ModelSerializer):
        modules = serializers.SerializerMethodField()
        class Meta:
            model = TrainPlan
            exclude = ('user',)

        class ModulesSeriazlier(serializers.Serializer):
            name = serializers.CharField()
            id = serializers.IntegerField()

        def get_modules(self, obj: TrainPlan):
            queryset = TrainModule.objects.filter(planmodule__plan=obj)
            serializer = self.ModulesSeriazlier(queryset, many=True)
            return serializer.data

    class InputSerializer(serializers.ModelSerializer):
        user = serializers.SlugRelatedField(slug_field='id', read_only=True)
        modules = serializers.ListField(child=serializers.IntegerField())
        id = IntegerField(required=False)

        class Meta:
            model = TrainPlan
            fields = ('name',
                      'modules',
                      'cycle',
                      'user',
                      'id')

        def create(self, validated_data: dict):
            modules = validated_data.pop("modules", None)
            try:
                plan = TrainPlan.objects.create(**validated_data)
            except IntegrityError:
                raise serializers.ValidationError(
                    {"detail": f"Cycle {validated_data['cycle']} is already set to other plan"})
            if modules is not None:
                for module_id in modules:
                    try:
                        module = TrainModule.objects.get(pk=module_id)
                    except TrainModule.DoesNotExist:
                        raise serializers.ValidationError(
                            {"detail": f"Module with id {module_id} does not exist"})
                    PlanModule.objects.create(plan=plan, module=module)
            return plan

    def create(self, request, *args, **kwargs):
        serialzier = self.get_serializer(data=request.data)
        serialzier.is_valid(raise_exception=True)
        obj = serialzier.save(user=self.request.user)
        result = self.OutputSerializer(obj)
        return Response(data=result.data, status=201)

    @action(detail=False, methods=['get'])
    def all(self, request) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def current(self, request) -> Response:
        """
        If there is a plan that matches current cycle 200 is returned with this plan \n
        Otherwise 201 is returned with all plans
        """
        try:
            queryset = self.get_queryset().get(cycle=self.request.user.current_cycle)
        except TrainPlan.DoesNotExist:
            queryset = self.get_queryset()
            serializer = self.get_serializer_class()(queryset, many=True)
            return Response(serializer.data, status=201)
        serializer = self.get_serializer_class()(queryset, many=False)
        return Response(serializer.data, status=200)
        

    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    serializer_class = OutputSerializer

    def get_queryset(self) -> QuerySet:
        return TrainPlan.objects.filter(user=self.request.user)

    def get_serializer_class(self) -> serializers.Serializer:
        if self.request.method == 'GET':
            return self.OutputSerializer
        return self.InputSerializer


class ExercisesList(generics.ListAPIView):

    class OutputSerializer(serializers.ModelSerializer):

        class Meta:
            model = Exercise
            fields = '__all__'

    serializer_class = OutputSerializer
    queryset = Exercise.objects.all()


class CreateTestData(APIView):
    def get(self, request: Request):
        MusclePart.objects.all().delete()
        biceps = MusclePart.objects.create(name="biceps")
        chest = MusclePart.objects.create(name="klata")
        Exercise.objects.all().delete()
        bs = Exercise.objects.create(
            muscle_part=biceps, name="Biceps sztanga", max_weight=150)
        bh = Exercise.objects.create(
            muscle_part=biceps, name="Biceps hantle", max_weight=150)
        ks = Exercise.objects.create(
            muscle_part=chest, name="Klata sztanga", max_weight=200)
        kh = Exercise.objects.create(
            muscle_part=chest, name="Klata hantle", max_weight=200)
        kc = Exercise.objects.create(
            muscle_part=chest, name="Klata coś", max_weight=200)
        user = User.objects.get(email=request.query_params.get('user'))
        TrainModule.objects.all().delete()
        t1 = TrainModule.objects.create(name="t1",
                                        user=user, exercise=bs, series=4, weight=35, level_weight_increase=2.5, reps=[12, 12, 12, 8])  # 23 lv
        t2 = TrainModule.objects.create(name="t2",
                                        user=user, exercise=bh, series=3, weight=20, level_weight_increase=2.5, reps=[8, 8, 12])  # 13 lv
        t3 = TrainModule.objects.create(name="t3",
                                        user=user, exercise=kh, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 8])  # 20 lv
        t4 = TrainModule.objects.create(name="t4",
                                        user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        t5 = TrainModule.objects.create(name="t5",
                                        user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        t6 = TrainModule.objects.create(name="t6",
                                        user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        t7 = TrainModule.objects.create(name="t7",
                                        user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        t8 = TrainModule.objects.create(name="t8",
                                        user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        t8 = TrainModule.objects.create(name="t9",
                                        user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        t8 = TrainModule.objects.create(name="t10",
                                        user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        p1 = TrainPlan.objects.create(name="plan1", user=user)
        p1 = TrainPlan.objects.create(name="plan2", user=user)
        p1 = TrainPlan.objects.create(name="plan3", user=user)
        p1 = TrainPlan.objects.create(name="plan4", user=user)
        p1 = TrainPlan.objects.create(name="plan5", user=user)
        p1 = TrainPlan.objects.create(name="plan6", user=user)
        pm1 = PlanModule.objects.create(module=t1, plan=p1)
        pm2 = PlanModule.objects.create(module=t2, plan=p1)
        pm3 = PlanModule.objects.create(module=t3, plan=p1)
        pm4 = PlanModule.objects.create(module=t4, plan=p1)
        TrainHistory.objects.create(plan_module=pm1, reps=[8, 8, 8, 8])
        TrainHistory.objects.create(plan_module=pm2, reps=[4, 4, 4])
        TrainHistory.objects.create(plan_module=pm3, reps=[6, 6, 6])
        TrainHistory.objects.create(plan_module=pm4, reps=[8, 8, 3])
        return Response(status=200)
