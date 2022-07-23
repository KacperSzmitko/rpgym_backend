from typing import Iterable
from app.models import Exercise, MusclePart


def muscles_list() -> Iterable[MusclePart]:
    return MusclePart.objects.all()
