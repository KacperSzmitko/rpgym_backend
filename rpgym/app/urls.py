from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views import PlanViewSet, MusclePartsView, MuscleLevelList, TrainModuleViewSet, CreateTestData, ExercisesList, TrainStartView

app_name = "app"
router = DefaultRouter()

router.register(r'muscle_parts', MusclePartsView, basename='user')
router.register(r'train_module', TrainModuleViewSet, basename='train_module')
router.register(r'plan', PlanViewSet, basename='plan')
urlpatterns = [
    path("", include(router.urls)),
    path("muscle_levels/", MuscleLevelList.as_view()),
    path("exercises/", ExercisesList.as_view()),
    path("test_data/", CreateTestData.as_view()),
    path("train/start/", TrainStartView.as_view()),
]
