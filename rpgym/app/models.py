from datetime import datetime
from django.db import models
from users.models import User
from django.core import validators


class MusclePart(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self) -> str:
        return self.name


class Exercise(models.Model):
    muscle_part = models.ForeignKey(MusclePart, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=128, unique=True)
    max_weight = models.DecimalField(default=0, decimal_places=2, max_digits=5)

    def __str__(self) -> str:
        return f"{self.pk}. {self.name}"


class TrainModule(models.Model):
    name = models.CharField(max_length=32, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True)
    series = models.IntegerField()
    weight = models.DecimalField(decimal_places=2, max_digits=5)
    level_weight_increase = models.DecimalField(default=0, decimal_places=2, max_digits=5)
    current_level = models.IntegerField(default=0)
    reps = models.JSONField()
    progress = models.DecimalField(default=0, decimal_places=2, max_digits=4)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)

    def increase_level(self):
        self.weight += self.level_weight_increase
        self.progress = 0
        return self

    def __str__(self) -> str:
        return str(self.pk)

    class Meta:
        ordering = ["-creation_date", "pk"]

    def save(self, *args, **kwargs) -> None:
        self.current_level = int((self.weight / self.exercise.max_weight) * 100)
        return super().save(*args, **kwargs)


# class TrainUnitReps(models.Model):
#     train_unit = models.ForeignKey(TrainUnit, on_delete=models.CASCADE)
#     reps = models.IntegerField()

#     # class Meta:
#     #     indexes = [models.Index(fields=["train_unit"])]


class TrainPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=128)
    cycle = models.IntegerField(default=None, null=True, unique=True, validators=[validators.MinValueValidator(0)])

    def __str__(self) -> str:
        return self.name


class PlanModule(models.Model):
    module = models.ForeignKey(TrainModule, on_delete=models.CASCADE)
    plan = models.ForeignKey(TrainPlan, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    order_in_plan = models.IntegerField()

    def __str__(self) -> str:
        return str(self.pk)

    class Meta:
        unique_together = (('plan', 'module',), ('plan', 'order_in_plan',),)


class TrainHistory(models.Model):
    plan_module = models.ForeignKey(PlanModule, on_delete=models.CASCADE, related_name="history", null=True)
    date = models.DateTimeField(auto_now_add=True)
    reps = models.JSONField(default=None, null=True)

    def save(self, *args, **kwargs) -> None:
        """
        Every time we end module, recalcualte progress and current level
        """
        max_reps, reps_diff = 0, 0
        for module_reps, train_reps in zip(self.plan_module.module.reps, self.reps):
            x = module_reps - train_reps
            max_reps += module_reps
            if x > 0:
                reps_diff += x
        module = self.plan_module.module
        if reps_diff == 0:
            module = module.increase_level()
        else:
            module.progress = reps_diff / max_reps
        module.save()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["-date"]

    def __str__(self) -> str:
        return str(self.pk)


# class HistoryUnitReps(models.Model):
#     train_unit = models.ForeignKey(TrainUnit, on_delete=models.CASCADE)
#     train_history = models.ForeignKey(TrainHistory, on_delete=models.CASCADE)
#     reps = models.IntegerField()


# class HistoryUnit(models.Model):
#     train_unit = models.ForeignKey(TrainUnit, on_delete=models.CASCADE)
#     train = models.ForeignKey(TrainHistory, on_delete=models.CASCADE)
