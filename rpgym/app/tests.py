from statistics import mean
from django.test import TestCase
from django.test import Client
from attrs import define
import json
from users.models import User
from app.models import MusclePart, Exercise, TrainModule, TrainPlan, PlanModule, TrainHistory
# Create your tests here.

AUTH_URL = "/api/v1/auth/token/"


class AppTestCases(TestCase):
    BASE_API_URL = "/api/v1/app/"

    @define(slots=False)
    class User:
        email: str
        password: str
        token: str = ""

    def obtain_token(self):
        """
        Obtain a token, and save user id and this token in user instance
        """
        response = self.client.post(
            AUTH_URL, self.user.__dict__, content_type="application/json")
        return response.json()["access"]

    def create_user(self):
        self.client.post("/api/v1/users/", self.user.__dict__,
                         content_type="application/json")

    def create_objects(self):
        biceps = MusclePart.objects.create(name="biceps")
        chest = MusclePart.objects.create(name="klata")
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
        user = User.objects.get()
        t1 = TrainModule.objects.create(
            user=user, exercise=bs, series=4, weight=35, level_weight_increase=2.5, reps=[12, 12, 12, 8])  # 23 lv
        t2 = TrainModule.objects.create(
            user=user, exercise=bh, series=3, weight=20, level_weight_increase=2.5, reps=[8, 8, 12])  # 13 lv
        t3 = TrainModule.objects.create(
            user=user, exercise=kh, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 8])  # 20 lv
        t4 = TrainModule.objects.create(
            user=user, exercise=ks, series=3, weight=40, level_weight_increase=2.5, reps=[12, 12, 12])  # 20 lv
        p1 = TrainPlan.objects.create(name="plan1")
        pm1 = PlanModule.objects.create(module=t1, plan=p1)
        pm2 = PlanModule.objects.create(module=t2, plan=p1)
        pm3 = PlanModule.objects.create(module=t3, plan=p1)
        pm4 = PlanModule.objects.create(module=t4, plan=p1)
        TrainHistory.objects.create(plan_module=pm1, reps=[8, 8, 8, 8])
        TrainHistory.objects.create(plan_module=pm2, reps=[4, 4, 4])
        TrainHistory.objects.create(plan_module=pm3, reps=[6, 6, 6])
        TrainHistory.objects.create(plan_module=pm4, reps=[8, 8, 3])

    def setUp(self) -> None:
        self.client = Client()
        self.user = self.User("test@wp.pl", "Test1234")
        self.create_user()
        self.user.token = self.obtain_token()
        self.client = Client(
            HTTP_AUTHORIZATION="Bearer {}".format(self.user.token))

    def test_get_muslce_levels(self):
        self.create_objects()
        response = self.client.get(
            self.BASE_API_URL + "muscle_levels/", content_type="application/json").json()
        for muscle in response:
            if muscle['muscle_name'] == 'biceps':
                self.assertEqual(muscle['level'], 18)
                self.assertEqual(muscle['progress'], 0.42)
            if muscle['muscle_name'] == 'klata':
                self.assertEqual(muscle['level'], 20)
                self.assertEqual(muscle['progress'], 0.45)
